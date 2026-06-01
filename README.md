# DevUtils API

A developer utility API with zero external dependencies (pure Python stdlib). Ready for deployment and RapidAPI marketplace.

## Deployed URL

**Base URL:** `https://devutils-api-production-5cec.up.railway.app`

## Authentication

Send `X-Api-Key` header with every request. Default key: `devutils-secret-2ae7436568540215`

## Endpoints

### Health
```
GET /health
```

### QR Code
```
GET /qr/generate?data=...&size=10&border=4&fill_color=%23000000&back_color=%23FFFFFF
```

### Text Utilities
```
GET /text/slugify?text=...&separator=-
GET /text/hash?text=...&algorithm=sha256|md5|sha1|sha512
GET /text/case?text=...&to=upper|lower|title|camel|snake|kebab
GET /text/count?text=...
```

### Data Utilities
```
GET /data/uuid
GET /data/base64/encode?text=...
GET /data/base64/decode?text=...
POST /data/json/validate  (JSON body)
```

## Quick Test

```bash
API_KEY="devutils-secret-2ae7436568540215"
BASE="https://devutils-api-production-5cec.up.railway.app"

curl -H "X-Api-Key: $API_KEY" $BASE/health
curl -H "X-Api-Key: $API_KEY" "$BASE/text/hash?text=hello&algorithm=sha256"
curl -H "X-Api-Key: $API_KEY" "$BASE/data/uuid"
```

## Deployment

The API runs on Railway. With a Dockerfile present, Railway builds and deploys automatically.

## Architecture

- Zero external dependencies — uses only Python standard library
- QR codes generated with pure-Python algorithm (no Pillow/qrcode packages)
- PNG images generated manually (no Pillow/PIL needed)
- Built-in API key authentication
- CORS headers for browser access
