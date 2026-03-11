# PDF Host & Preview (Streamlit)

Session-based app: upload PDFs, preview them, view converted text, chat to query the PDF via your backend API, and jump to a page from the converted view.

## Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Project layout

- **`app.py`** – Entry point; composes sidebar and tabs.
- **`config.py`** – Backend base URL and paths from env.
- **`state.py`** – Session state init and helpers.
- **`pdf_utils.py`** – PDF text extraction and `add_upload`.
- **`components/`** – UI components (sidebar, preview tab, converted tab, chat tab, health status).
- **`services/`** – Backend calls: health check and chat API.

## Features

- **Sessioned by browser**: Each tab/window has its own session; uploads are stored only in that session (no database).
- **Upload PDF**: Sidebar upload; add to session and select which PDF to view.
- **Preview PDF**: Tab with embedded viewer; scroll-to-page from Converted tab.
- **Converted (text)**: Per-page text, download as `.txt`, and “Go to page N in PDF” to jump the viewer.
- **Chat**: Interactive chat tab; each message is sent to your backend API with the current PDF context (and optional `pdf_id`). Backend must be running and reachable (see env below).
- **Backend health**: Sidebar shows a **green dot** when the backend is up and **latency in ms**; red when the service is down or unreachable.

## Backend API

The app calls your existing backend for:

1. **Health** – `GET {PDF_QUERY_API_URL}{HEALTH_PATH}` (default `GET http://localhost:8000/health`). Any 2xx is “up”; latency is measured.
2. **Chat / query** – `POST {PDF_QUERY_API_URL}{CHAT_PATH}` (default `POST http://localhost:8000/query`) with JSON body:
   - `query` (required): user message
   - `context` (optional): full extracted text of the current PDF
   - `pdf_id` (optional): current upload id

Response is expected to be JSON, e.g. `{"answer": "..."}` or `{"response": "..."}`; the app looks for `answer`, `response`, or `text` and falls back to stringifying the body.

### Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `PDF_QUERY_API_URL` | `http://localhost:8000` | Backend base URL |
| `HEALTH_PATH` | `/health` | Health endpoint path |
| `CHAT_PATH` | `/query` | Chat/query endpoint path |

## Database

This app does **not** use a database. PDFs and text live only in Streamlit session state. To persist uploads or chat history across sessions, a database (e.g. SQLite) can be added.
