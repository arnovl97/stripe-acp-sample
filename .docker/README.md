# Dockerfiles for ACP Demo Services

This folder contains Dockerfiles for deploying the Mock Stripe SPT server and Seller Backend to Coolify or any Docker-compatible platform.

## Files

- `Dockerfile.mock-stripe-spt` - Mock Stripe Shared Payment Token server (Python/Flask)
- `Dockerfile.seller-backend` - Seller Backend API (Node.js/TypeScript/Express)

## Usage with Coolify

### Mock Stripe SPT Server

1. In Coolify, create a new application
2. Select "Dockerfile" as the build method
3. Set the Dockerfile path to: `.docker/Dockerfile.mock-stripe-spt`
4. Set the build context to the repository root
5. Configure environment variables:
   - `MOCK_STRIPE_SPT_PORT=8001` (or your desired port)
6. Expose port 8001 (or your configured port)

### Seller Backend

1. In Coolify, create a new application
2. Select "Dockerfile" as the build method
3. Set the Dockerfile path to: `.docker/Dockerfile.seller-backend`
4. Set the build context to the repository root
5. Configure environment variables:
   - `PORT=3000` (or your desired port)
   - `MOCK_STRIPE_SPT_URL=http://your-mock-spt-server:8001` (URL to your Mock SPT server)
   - `SELLER_API_KEY=sk_test_...` (Your Stripe API key)
6. Expose port 3000 (or your configured port)

## Environment Variables

### Mock Stripe SPT Server
- `MOCK_STRIPE_SPT_PORT` - Port to run the server on (default: 8001)

### Seller Backend
- `PORT` - Port to run the server on (default: 3000)
- `MOCK_STRIPE_SPT_URL` - Full URL to the Mock Stripe SPT server (required)
- `SELLER_API_KEY` - Stripe secret API key (required)

## Building Locally

### Mock Stripe SPT
```bash
docker build -f .docker/Dockerfile.mock-stripe-spt -t mock-stripe-spt .
docker run -p 8001:8001 -e MOCK_STRIPE_SPT_PORT=8001 mock-stripe-spt
```

### Seller Backend
```bash
docker build -f .docker/Dockerfile.seller-backend -t seller-backend .
docker run -p 3000:3000 \
  -e PORT=3000 \
  -e MOCK_STRIPE_SPT_URL=http://localhost:8001 \
  -e SELLER_API_KEY=sk_test_... \
  seller-backend
```

## Notes

- Both Dockerfiles use multi-stage builds where applicable to minimize image size
- Health checks are included for both services
- The Seller Backend Dockerfile builds TypeScript during the build process
- Make sure to configure the `MOCK_STRIPE_SPT_URL` correctly in Seller Backend to point to your deployed Mock SPT server
- If services are on the same Coolify instance, you can use internal service names for `MOCK_STRIPE_SPT_URL`

