# DevUtils API

A lightweight developer utility API — **zero external dependencies**, uses only Python standard library. Ready to deploy and sell on [RapidAPI](https://rapidapi.com/).

## Features

| Category | Endpoints |
|---|---|
| **QR Code** | Generate QR codes from any text or URL |
| **Text Utilities** | Slugify, hash (md5/sha1/sha256/sha512), case conversion, text analysis |
| **Data Utilities** | UUID v4 generation, Base64 encode/decode, JSON validation |

## Quick Start

```bash
# No installation needed! Just run:
python main.py

# Or set your API key:
API_KEY=your-secret-key python main.py
```

Then open http://localhost:8080/docs for the API documentation.

## Deployment

### Deploy to Railway (free)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/-)

1. Fork/push this repo to GitHub
2. Go to [Railway](https://railway.app/) → New Project → Deploy from GitHub repo
3. Set environment variable `API_KEY` to a random string
4. Railway auto-detects Python and starts the server

Or deploy manually:

```bash
# Install Railway CLI
npm i -g @railway/cli

# Login and deploy
railway login
railway up
railway domain  # Get your public URL
```

### Deploy to Render

1. Push to GitHub
2. Create new Web Service on Render
3. Set start command: `python main.py`
4. Add `API_KEY` env variable

## Endpoints

### Health

```
GET /health
```
Returns `{"status": "healthy"}`

### QR Code Generation

```
GET /qr/generate?data=https://example.com&size=10&border=4&fill_color=%23000000&back_color=%23FFFFFF
```

Returns a PNG image. Parameters:

| Param | Required | Default | Description |
|---|---|---|---|
| `data` | Yes | — | Text or URL to encode |
| `size` | No | 10 | Box size per module (pixels) |
| `border` | No | 4 | Border width (modules) |
| `fill_color` | No | #000000 | Foreground color (hex) |
| `back_color` | No | #FFFFFF | Background color (hex) |

### Text Slugify

```
GET /text/slugify?text=Hello World&separator=-
```

Response: `{"original": "Hello World", "slug": "hello-world", "separator": "-"}`

### Text Hash

```
GET /text/hash?text=hello&algorithm=sha256
```

Algorithms: `md5`, `sha1`, `sha256`, `sha512`

### Case Conversion

```
GET /text/case?text=hello_world&to=camel
```

Options: `upper`, `lower`, `title`, `camel`, `snake`, `kebab`

### Text Analysis

```
GET /text/count?text=Hello world. How are you?
```

Returns character, word, sentence, and paragraph counts.

### UUID Generation

```
GET /data/uuid
```

Returns: `{"uuid": "550e8400-e29b-41d4-a716-446655440000", "version": 4}`

### Base64 Encode/Decode

```
GET /data/base64/encode?text=hello world
GET /data/base64/decode?text=aGVsbG8gd29ybGQ=
```

### JSON Validation

```
POST /data/json/validate
Content-Type: application/json

{"name": "test", "value": 42}
```

## Authentication

Set the `API_KEY` environment variable. Clients pass it via the `X-Api-Key` header. When proxied through RapidAPI, it's automatically sent as `X-RapidAPI-Proxy-Secret`.

## Sell on RapidAPI

1. **Deploy** the API to Railway/Render and get your public URL
2. Go to [RapidAPI Provider Dashboard](https://rapidapi.com/providers/dashboard)
3. Click **"Add New API"**
4. Enter your public URL as the **Base URL**
5. Configure these endpoints in RapidAPI

### Recommended Pricing

| Tier | Price | Requests/Month | Rate Limit |
|---|---|---|---|
| Free | $0 | 100 | 10/min |
| Basic | $4.99/mo | 5,000 | 60/min |
| Pro | $9.99/mo | 20,000 | 300/min |
| Ultra | $19.99/mo | Unlimited | 1000/min |

### Expected Monthly Revenue

- At $4.99/mo with 5-10 subscribers: **$25-50/mo**
- At $9.99/mo with 10-20 subscribers: **$100-200/mo** (reach $100 in first month)

## License

MIT
