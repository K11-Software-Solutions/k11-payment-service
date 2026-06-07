from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import httpx, os

app = FastAPI(
    title="Payment Service",
    description="Processes payments for the K11 platform. Consumes user-service and order-service.",
    version="1.0.0",
)

USER_SERVICE_URL  = os.getenv("USER_SERVICE_URL",  "http://user-service:8000")
ORDER_SERVICE_URL = os.getenv("ORDER_SERVICE_URL", "http://order-service:8000")


class Payment(BaseModel):
    id: str
    user_id: str
    order_id: str
    amount: float
    currency: str = "USD"
    status: str = "pending"


class CreatePayment(BaseModel):
    user_id: str
    order_id: str
    amount: float
    currency: str = "USD"


@app.get("/api/v1/payments/{id}", response_model=Payment, tags=["payments"])
async def get_payment(id: str):
    """Get a payment by ID."""
    raise HTTPException(status_code=404, detail="Payment not found")


@app.post("/api/v1/payments", response_model=Payment, status_code=201, tags=["payments"])
async def create_payment(body: CreatePayment):
    """Initiate a payment. Validates user identity and order existence."""
    async with httpx.AsyncClient() as client:
        user_resp = await client.get(f"{USER_SERVICE_URL}/api/v2/users/{body.user_id}")
        if user_resp.status_code == 404:
            raise HTTPException(status_code=422, detail="User not found")
        order_resp = await client.get(f"{ORDER_SERVICE_URL}/api/v1/orders/{body.order_id}")
        if order_resp.status_code == 404:
            raise HTTPException(status_code=422, detail="Order not found")
    return Payment(id="generated-id", **body.model_dump())


@app.get("/health")
async def health():
    return {"status": "ok", "service": "payment-service", "version": "1.0.0"}
