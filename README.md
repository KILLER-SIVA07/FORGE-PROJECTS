# Enterprise QR Visitor Management API (Starter)

Production-oriented backend starter implementing:
- JWT auth
- RBAC (Admin, Security, Staff, Visitor)
- Event management
- Registration + policy-based approval logic
- Gate actions (checkin/checkout/reject)
- Basic audit trail entities

## Run
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## Test
```bash
pytest -q
```
