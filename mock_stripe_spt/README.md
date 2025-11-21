# Mock Stripe SPT Server

Simple Flask server that mocks Stripe's Shared Payment Token API for demo purposes.

## Purpose

Since ACP with Stripe's Shared Payment Token is not available in Europe yet, this server simulates the SPT flow:
1. Receives payment method details
2. Generates a unique SPT ID
3. Stores the mapping in memory
4. Allows retrieval of payment details via SPT ID

## Installation

```bash
cd mock_stripe_spt
pip install -r requirements.txt
```

## Running

```bash
python server.py
```

Server will start on `http://localhost:8001`

## Endpoints

### POST /v1/shared_payment/issued_tokens
Create a Shared Payment Token (called by chat_backend)

**Request:**
```bash
curl -X POST http://localhost:8001/v1/shared_payment/issued_tokens \
  -d "payment_method=pm_test_card" \
  -d "usage_limits[currency]=usd" \
  -d "usage_limits[max_amount]=5000" \
  -d "usage_limits[expires_at]=1234567890"
```

**Response:**
```json
{
  "id": "spt_abc123...",
  "object": "shared_payment.issued_token",
  "created": 1234567890,
  "livemode": false
}
```

### GET /v1/shared_payment/granted_tokens/{spt_id}
Retrieve payment details for an SPT (called by seller_backend)

**Request:**
```bash
curl http://localhost:8001/v1/shared_payment/granted_tokens/spt_abc123
```

**Response:**
```json
{
  "id": "spt_abc123",
  "payment_method": "pm_test_card",
  "usage_limits": {
    "currency": "usd",
    "max_amount": 5000,
    "expires_at": 1234567890
  },
  "status": "active"
}
```

### GET /health
Health check endpoint

## Architecture

```
Chat Backend → Mock SPT Server (create SPT, store payment method)
                      ↓
                 Store in memory
                      ↓
Seller Backend → Mock SPT Server (retrieve payment method)
                      ↓
                 Stripe API (process payment in test mode)
```

**Purpose:**
- Securely transfer payment details from chat backend to seller backend
- Payment details never exposed to LLM (only SPT token is visible)
- Seller backend uses retrieved payment method to call real Stripe API

