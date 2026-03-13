"""
PDF Host & Preview: top bar, then full-width resizable left | right columns.
"""
import streamlit as st
from streamlit_adjustable_columns import adjustable_columns

from config import HEALTH_CHECK_INTERVAL_SEC, SIDEBAR_MAX_WIDTH
from datastore import KEY_ACTIVE_MAIN_TAB, KEY_GO_TO_NOTES_TAB, KEY_SCROLL_TO_PAGE
from state import ensure_session_state, get_current_upload, clear_scroll_target
from components import render_top_bar, render_left_column, render_preview_tab, render_converted_tab, render_template_tab

st.set_page_config(
    page_title="PDF Host & Preview",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Limit sidebar max width when expanded (drag to resize)
if SIDEBAR_MAX_WIDTH:
    st.markdown(
        f'<style>'
        f'body section[data-testid="stSidebar"] {{  max-width: {SIDEBAR_MAX_WIDTH} !important; }} '
        f'section[data-testid="stSidebar"] > div {{  max-width: {SIDEBAR_MAX_WIDTH} !important; }}'
        f'</style>',
        unsafe_allow_html=True,
    )

ensure_session_state()

# When Insert clicked in chat, switch main panel to Notes tab
if st.session_state.pop(KEY_GO_TO_NOTES_TAB, None):
    st.session_state[KEY_ACTIVE_MAIN_TAB] = 2

# Top bar (session + backend health + Refresh). Fragment reruns every HEALTH_CHECK_INTERVAL_SEC so health check runs on that interval.
@st.fragment(run_every=HEALTH_CHECK_INTERVAL_SEC)
def _top_bar_with_health():
    render_top_bar()

_top_bar_with_health()

# Whole area below top bar is resizable: drag the handle between left and right
st.markdown("""
<style>
[data-testid="stSidebarHeader"] {
    height: 0.5rem;
    padding: 0rem;
    margin: 0rem;
}
[data-testid="stSidebarCollapseButton"]{
    position:absolute;
    display: none;
    top:3px;
    right:10px;
    z-index:1000;
}
[data-testid="stMainBlockContainer"] {
    padding: 45px 50px;
}
/* User chat message: show icon on the right */
[data-testid="stChatMessage"] {
    display: flex !important;
}
[data-testid="stChatMessage"][aria-label="User"],
[data-testid="stChatMessage"][aria-label="user"] {
    flex-direction: row-reverse !important;
}

</style>
""", unsafe_allow_html=True)

render_left_column()

current = get_current_upload()
if current is None:
    st.markdown("### Preview")
else:
    st.markdown(f"### 📄 {current['name']}")

tab_index = st.radio(
    "Panel",
    options=[0, 1, 2],
    format_func=lambda i: ["Preview PDF", "Analyzed PDF", "Notes"][i],
    key=KEY_ACTIVE_MAIN_TAB,
    horizontal=True,
    label_visibility="collapsed",
)
if tab_index == 0:
    if current is None:
        st.info("Upload a PDF in the left column to get started. Your data stays in this session only.")
    else:
        render_preview_tab(current)
elif tab_index == 1:
    if current is None:
        st.info("Select a PDF to see converted text here.")
    else:
        render_converted_tab(current)
else:
    render_template_tab(current)

if current is not None:
    clear_scroll_target()
