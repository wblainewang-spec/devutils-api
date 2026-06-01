# DevUtils API

A developer utility API with zero external dependencies (pure Python stdlib). QR code generation, text utilities, data utilities, and more.

**Deployed URL:** https://devutils-api-production-5cec.up.railway.app

## Quick Start

```bash
API_KEY="devutils-secret-2ae7436568540215"
BASE="https://devutils-api-production-5cec.up.railway.app"

# Health check
curl -H "X-Api-Key: $API_KEY" $BASE/health

# Generate UUID
curl -H "X-Api-Key: $API_KEY" $BASE/data/uuid

# Text utilities
curl -H "X-Api-Key: $API_KEY" "$BASE/text/hash?text=hello"
curl -H "X-Api-Key: $API_KEY" "$BASE/text/slugify?text=Hello%20World"
curl -H "X-Api-Key: $API_KEY" "$BASE/text/count?text=Hello+world!"

# Base64
curl -H "X-Api-Key: $API_KEY" "$BASE/data/base64/encode?text=hello"

# QR code
curl -H "X-Api-Key: $API_KEY" -o qr.png "$BASE/qr/generate?data=https://example.com"
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| GET | `/docs` | HTML documentation |
| GET | `/qr/generate` | Generate QR code PNG |
| GET | `/text/slugify` | URL-friendly slug |
| GET | `/text/hash` | MD5 / SHA1 / SHA256 / SHA512 |
| GET | `/text/case` | Case conversion (camel, snake, etc.) |
| GET | `/text/count` | Word/char/sentence count |
| GET | `/data/uuid` | UUID v4 generator |
| GET | `/data/base64/encode` | Base64 encode |
| GET | `/data/base64/decode` | Base64 decode |
| POST | `/data/json/validate` | JSON validation |

## Deploy to RapidAPI Marketplace

1. Go to [https://rapidapi.com/studio](https://rapidapi.com/studio) and sign in with your GitHub account
2. Click **Add API** → **Import OpenAPI**
3. Upload `outputs/openapi.yaml` from this project
4. Set the API to **Private** or **Public** under General tab
5. Configure plans under Monetize tab (free + paid tiers)
6. Submit for approval

### Recommended Pricing

| Plan | Price | Rate Limit |
|------|-------|------------|
| Free | $0/mo | 100 requests/day |
| Basic | $5/mo | 1,000 requests/day |
| Pro | $20/mo | 10,000 requests/day |
| Ultra | $50/mo | Unlimited |

## Architecture

- **Zero external dependencies** — uses only Python standard library
- **QR codes** — pure-Python QR code generator (no Pillow/qrcode packages)
- **PNG images** — hand-written PNG encoder (no Pillow)
- **Auth** — API key authentication (X-Api-Key header)
- **CORS** — enabled for all origins

## Deployment

Deployed on Railway using Dockerfile. See `railway.json` for configuration.

```bash
railway up --service devutils-api
```
