"""Left column: PDF upload (process file) and Chat."""
from __future__ import annotations

import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

import streamlit as st

from datastore import (
    KEY_CONVERTED_IMAGES,
    KEY_FROM_PAGE,
    KEY_GO_TO_CHAT,
    KEY_LEFT_TAB,
    KEY_PENDING_PROCESS,
    KEY_PROMPT_EDITOR,
    KEY_SELECTED_ID,
    KEY_TEXT_OUTPUT_ONLY,
    KEY_TO_PAGE,
    KEY_UPLOADS,
    KEY_UPLOADER_RESET,
    LOADING_PLACEHOLDER,
)
from state import get_current_upload, get_or_create_conversation, get_backend_base_url, get_streamlit_app_url
from pdf_utils import add_upload
from components.chat_tab import render_chat_tab
from services.chat_api import pdf_detail_from_external
from services.langfuse_prompt import get_prompt_from_langfuse

KEY_DEBUG_REQUEST_LOGS = "debug_request_logs"


def _debug_log(message: str) -> None:
    """Write request debug info to server logs and keep recent entries in session for UI."""
    ts = datetime.now().strftime("%H:%M:%S")
    line = f"[{ts}] {message}"
    print(line, flush=True)
    logs = st.session_state.get(KEY_DEBUG_REQUEST_LOGS, [])
    logs.append(line)
    st.session_state[KEY_DEBUG_REQUEST_LOGS] = logs[-80:]


def _parse_image_response(response: object, pdf_id: str) -> list[bytes]:
    """Parse backend response into list of image bytes per page. Returns [] on parse failure."""
    images: list[bytes] = []
    try:
        if isinstance(response, bytes):
            if response:
                images.append(response)
            return images
        if isinstance(response, dict):
            # "images": [base64, ...], "image": base64, or "summarized_images": [...]
            raw = (
                response.get("images")
                or (response.get("image") and [response["image"]])
                or response.get("summarized_images")
            )
            if not raw:
                return []
            for item in raw:
                if isinstance(item, bytes):
                    images.append(item)
                elif isinstance(item, str):
                    images.append(base64.b64decode(item))
                else:
                    images.append(base64.b64decode(str(item)))
            return images
        if isinstance(response, list):
            for item in response:
                if isinstance(item, bytes):
                    images.append(item)
                elif isinstance(item, str):
                    images.append(base64.b64decode(item))
                else:
                    images.append(base64.b64decode(str(item)))
            return images
    except Exception:
        pass
    return []


def _load_default_prompt_from_file() -> str:
    """Load prompt content from prompts/default.md (relative to project root). Returns "" if missing or on error."""
    try:
        path = Path(__file__).resolve().parent.parent / "prompts" / "default.md"
        if path.is_file():
            return path.read_text(encoding="utf-8").strip()
    except Exception:
        pass
    return ""


def _maybe_run_pending_process() -> None:
    """If Process-file inserted a Loading placeholder, run backend request(s) and replace it."""
    current = get_current_upload()
    pending_pdf = st.session_state.get(KEY_PENDING_PROCESS)
    if not (current and pending_pdf == current.get("id")):
        return

    conv = get_or_create_conversation(current["id"])
    if not (conv["messages"] and conv["messages"][-1].get("content") == LOADING_PLACEHOLDER):
        return

    prompt_prefix = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
    text_output_only = st.session_state.get(KEY_TEXT_OUTPUT_ONLY, True)
    from_page = max(1, st.session_state.get(KEY_FROM_PAGE, 1))
    to_page = st.session_state.get(KEY_TO_PAGE, 20)
    base_url = get_backend_base_url()
    external_loc = get_streamlit_app_url()
    pdf_id = current["id"]
    _debug_log(
        f"pending process start: pdf_id={pdf_id[:8]} text_output_only={text_output_only} from={from_page} to={to_page}"
    )

    def request_text() -> object:
        _debug_log("request_text: start")
        return pdf_detail_from_external(
            system_prompt=prompt_prefix or "",
            external_loc=external_loc,
            from_page=from_page,
            to_page=to_page,
            conversation_id=conv["conversation_id"],
            text_output_only=text_output_only,
            base_url=base_url,
        )

    def request_images() -> object:
        _debug_log("request_images: start")
        return pdf_detail_from_external(
            system_prompt="",
            external_loc=external_loc,
            conversation_id=None,
            text_output_only=False,
            from_page=from_page,
            to_page=to_page,
            base_url=base_url,
        )

    img_response: object = None
    try:
        if text_output_only:
            _debug_log("branch: text_output_only=True -> sending one request (text only)")
            response = request_text()
        else:
            _debug_log("branch: text_output_only=False -> sending two concurrent requests (text + images)")
            with ThreadPoolExecutor(max_workers=2) as executor:
                fut_text = executor.submit(request_text)
                fut_images = executor.submit(request_images)
                response = fut_text.result()
                _debug_log(f"request_text: done type={type(response).__name__}")
                img_response = fut_images.result()
                _debug_log(f"request_images: done type={type(img_response).__name__}")
        if isinstance(response, dict):
            answer = (
                response.get("summary")
                or response.get("summary_text")
                or response.get("answer")
                or response.get("response")
                or response.get("text")
                or (str(response) if response else None)
            )
        elif isinstance(response, list):
            answer = "\n".join(str(x) for x in response) if response else None
        else:
            answer = str(response) if response else None
        conv["messages"][-1]["content"] = answer or "(No response)"
        # Images: prefer summarized_images from same response (single request); else use img_response (second request)
        images_to_show = None
        if isinstance(response, dict) and response.get("summarized_images") is not None:
            _debug_log("images source: summarized_images from text response")
            images_to_show = _parse_image_response(response, pdf_id)
        if images_to_show is None and not text_output_only and img_response is not None:
            _debug_log("images source: separate image response")
            images_to_show = _parse_image_response(img_response, pdf_id)
        if images_to_show:
            if KEY_CONVERTED_IMAGES not in st.session_state:
                st.session_state[KEY_CONVERTED_IMAGES] = {}
            st.session_state[KEY_CONVERTED_IMAGES][pdf_id] = images_to_show
            _debug_log(f"stored images: count={len(images_to_show)}")
        else:
            _debug_log("stored images: none")
    except Exception as e:
        conv["messages"][-1]["content"] = f"Error: {e}"
        _debug_log(f"pending process error: {e}")
    st.session_state.pop(KEY_PENDING_PROCESS, None)
    _debug_log("pending process complete -> rerun")
    st.rerun()


def render_left_column() -> None:
    """Render the app sidebar. Session block, then Upload | Chat tabs."""
    with st.sidebar:
        if st.session_state[KEY_UPLOADS]:
            uploads = st.session_state[KEY_UPLOADS]
            selected_id = st.session_state.get(KEY_SELECTED_ID)
            default_idx = next((i for i, u in enumerate(uploads) if u["id"] == selected_id), 0)
            # No widget key: use index= so selection is driven by KEY_SELECTED_ID; unique label per doc so same file twice = two options
            idx = st.selectbox(
                "Select PDF",
                range(len(uploads)),
                format_func=lambda i: f"{uploads[i]['name']} ({uploads[i]['num_pages']} p.) · {uploads[i]['id'][:8]}",
                index=default_idx,
                label_visibility="collapsed",
            )
            st.session_state[KEY_SELECTED_ID] = uploads[idx]["id"]

        # Apply "go to Chat" from Process file click before radio is created (can't modify widget key after)
        if st.session_state.pop(KEY_GO_TO_CHAT, None):
            st.session_state[KEY_LEFT_TAB] = 1

        tab_index = st.radio(
            "Section",
            options=[0, 1],
            format_func=lambda i: ["Upload", "Chat"][i],
            key=KEY_LEFT_TAB,
            horizontal=True,
            label_visibility="collapsed",
        )
        # Run pending Process-file backend work regardless of which sidebar tab is currently visible.
        _maybe_run_pending_process()
        with st.expander("Request debug", expanded=False):
            logs = st.session_state.get(KEY_DEBUG_REQUEST_LOGS, [])
            if logs:
                st.code("\n".join(logs[-25:]), language="text")
            else:
                st.caption("No request logs yet.")
        if tab_index == 0:
            # Prompt section: default from prompts/default.md, then Langfuse when empty
            if KEY_PROMPT_EDITOR not in st.session_state:
                st.session_state[KEY_PROMPT_EDITOR] = ""
            current_prompt = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
            if not current_prompt:
                file_content = _load_default_prompt_from_file()
                if file_content:
                    st.session_state[KEY_PROMPT_EDITOR] = file_content
                else:
                    langfuse_content = get_prompt_from_langfuse()
                    if langfuse_content:
                        st.session_state[KEY_PROMPT_EDITOR] = langfuse_content
            with st.expander("Prompt (optional)", expanded=False):
                st.text_area(
                    "Edit prompt",
                    height=240,
                    key=KEY_PROMPT_EDITOR,
                    placeholder="Add optional context or instructions for your questions...",
                    label_visibility="collapsed",
                )

            uploader_key = f"pdf_uploader_{st.session_state[KEY_UPLOADER_RESET]}"
            uploaded_file = st.file_uploader("Choose a PDF", type=["pdf"], key=uploader_key)
            if uploaded_file is not None:
                col_from, col_to = st.columns(2)
                with col_from:
                    st.number_input("From", min_value=1, value=max(1, st.session_state.get(KEY_FROM_PAGE, 1)), key=KEY_FROM_PAGE)
                with col_to:
                    st.number_input("To", min_value=0, value=st.session_state.get(KEY_TO_PAGE, 20), key=KEY_TO_PAGE)
                col_btn, col_toggle = st.columns([1, 1])
                with col_btn:
                    if st.button("Process file", key="btn_process_file"):
                        # 1. Load the PDF and add user + assistant "Loading..." then switch to Chat; API runs on next run
                        add_upload(st.session_state, uploaded_file.name, uploaded_file.getvalue())
                        pdf_id = st.session_state[KEY_SELECTED_ID]
                        prompt_prefix = (st.session_state.get(KEY_PROMPT_EDITOR) or "").strip()
                        conv = get_or_create_conversation(
                            pdf_id,
                            initial_messages=[{"role": "user", "content": prompt_prefix}],
                        )
                        conv["messages"].append({"role": "assistant", "content": LOADING_PLACEHOLDER})
                        st.session_state[KEY_PENDING_PROCESS] = pdf_id
                        st.session_state[KEY_UPLOADER_RESET] += 1  # clear uploader
                        st.session_state[KEY_GO_TO_CHAT] = True  # switch to Chat on next run
                        st.rerun()
                with col_toggle:
                    st.checkbox(
                        "Text Output Only",
                        value=st.session_state.get(KEY_TEXT_OUTPUT_ONLY, True),
                        key=KEY_TEXT_OUTPUT_ONLY,
                    )
        else:
            render_chat_tab(get_current_upload())
