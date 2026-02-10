# Enterprise QR Visitor Management Platform

This repository contains both backend and frontend starter code for an enterprise-grade QR Visitor Management System.

## Backend (FastAPI)
Features:
- JWT auth
- RBAC (Admin, Security, Staff, Visitor)
- Event management
- Registration + policy-based approval logic
- Gate actions (checkin/checkout/reject)
- Basic audit trail entities

Run:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Test:
```bash
pytest -q
```

## Frontend (Next.js)
Frontend files are under `frontend/` with role-based dashboards.

Run:
```bash
cd frontend
npm install
npm run dev
```

Optional API base URL:
```bash
export NEXT_PUBLIC_API_BASE=http://127.0.0.1:8000
```
