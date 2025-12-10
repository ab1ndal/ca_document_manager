# CA Document Manager

Lightweight Autodesk ACC RFI dashboard with a modern light-mode UI, collapsible filter rail, and a dedicated login screen (blue theme). The login page is the first entry point and redirects you back to the dashboard after a successful Autodesk auth.

## Prerequisites

- Python 3.11+
- Node 18+ and npm
- Poetry (`pip install poetry`)
- Autodesk APS credentials

## Environment

Create `.env` in the repo root with:

```
APS_CLIENT_ID=your_client_id
APS_CLIENT_SECRET=your_client_secret
ACC_PROJECT_ID=your_project_id
# optional
APS_TOKEN_FILE=aps_token.json
APS_SERVER=localhost
```

Tokens are stored locally in `aps_token.json`.

## Install

```bash
poetry install
cd frontend
npm install
```

## Run (dev)

Terminal 1 (backend):

```bash
poetry run python -m backend.main
```

Terminal 2 (frontend):

```bash
cd frontend
npm run dev
```

Visit the Vite dev URL (default http://localhost:5173). If auth fails or no token is present, you’ll land on the blue login page. Click **Continue with Autodesk**, complete auth, and you’ll be routed to the main dashboard with filters on the left (~15%) and results on the right.

## Build frontend

```bash
cd frontend
npm run build
```

## Package desktop exe

```bash
poetry run pyinstaller ca_manager.spec --noconfirm --clean
```

## Tests

```bash
poetry run pytest
```
