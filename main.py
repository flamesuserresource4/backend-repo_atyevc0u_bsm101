import os
from datetime import datetime, timezone
from typing import Optional, Dict, Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import db

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class UpsertPayload(BaseModel):
    client_id: str
    values: Dict[str, Any]


COLLECTION_MAP = {
    "bank_balance": "bankbalance",
    "expenses": "expense",
    "sales": "sale",
    "orders": "order",
    "reminders": "reminder",
}


@app.get("/")
def read_root():
    return {"message": "Smart Ledger Backend", "status": "ok"}


@app.get("/test")
def test_database():
    resp = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": "❌ Not Set",
        "database_name": "❌ Not Set",
        "connection_status": "Not Connected",
        "collections": [],
    }

    try:
        if db is not None:
            resp["database"] = "✅ Available"
            resp["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            resp["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"
            # Try listing collections
            try:
                resp["collections"] = db.list_collection_names()[:10]
                resp["database"] = "✅ Connected & Working"
                resp["connection_status"] = "Connected"
            except Exception as e:
                resp["database"] = f"⚠️ Connected but error: {str(e)[:80]}"
        else:
            resp["database"] = "❌ Database client not initialized"
    except Exception as e:
        resp["database"] = f"❌ Error: {str(e)[:80]}"

    return resp


@app.get("/api/dashboard/{client_id}")
def get_dashboard(client_id: str):
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")

    result = {}
    try:
        # fetch latest doc per collection for this client_id
        for api_table, coll in COLLECTION_MAP.items():
            doc = db[coll].find_one({"client_id": client_id}, sort=[("updated_at", -1)])
            if doc:
                doc["_id"] = str(doc["_id"])  # serialize
            result[api_table] = doc
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return result


@app.post("/api/upsert/{table}")
def upsert_table(table: str, payload: UpsertPayload):
    if table not in COLLECTION_MAP:
        raise HTTPException(status_code=404, detail="Unknown table")
    coll_name = COLLECTION_MAP[table]

    client_id = payload.client_id
    values = payload.values or {}

    if not client_id:
        raise HTTPException(status_code=400, detail="client_id required")

    # build update doc
    now = datetime.now(timezone.utc)
    update_doc = {**values, "client_id": client_id, "updated_at": now}

    try:
        db[coll_name].update_one(
            {"client_id": client_id},
            {"$set": update_doc},
            upsert=True,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
