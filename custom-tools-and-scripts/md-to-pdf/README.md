# md-to-pdf

Tiny FastAPI service that turns markdown into a PDF, returned as base64 inside JSON.
Used as a sidecar for the n8n SEO-audit workflow, but works standalone.

Listens on **port 8191**.

## API

`POST /convert`

Request body:
```json
{
  "markdown": "# Hello\n\nSome **bold** text.",
  "title": "My Document"
}
```

Response:
```json
{
  "pdf_base64": "JVBERi0xLjQK...",
  "filename": "My Document.pdf"
}
```

## Run it — pick one

### Option A: Local venv (simplest for dev)

```bash
cd custom-tools-and-scripts/md-to-pdf
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn server:app --host 0.0.0.0 --port 8191
```

Leave that terminal open. Stop with `Ctrl+C`.

### Option B: Docker (build & run, no Python on host needed)

```bash
cd custom-tools-and-scripts/md-to-pdf
docker build -t md-to-pdf .
docker run --rm -p 8191:8191 --name md-to-pdf md-to-pdf
```

Add `-d` instead of `--rm` to run detached. Stop with `docker stop md-to-pdf`.

## Quick test

```bash
curl -s -X POST http://localhost:8191/convert \
  -H 'Content-Type: application/json' \
  -d '{"markdown":"# Test\n\nHello world","title":"Test"}' \
  | python3 -c 'import sys,json,base64; open("test.pdf","wb").write(base64.b64decode(json.load(sys.stdin)["pdf_base64"]))' \
  && open test.pdf
```

## Use from n8n (running in Docker)

n8n containers can't reach `localhost` on the host directly — use `host.docker.internal`.

In your **HTTP Request** node:

- Method: `POST`
- URL: `http://host.docker.internal:8191/convert`
- Send Body: `JSON` → Specify Body: `Using Fields Below`
  - `markdown` → `={{ $json.output }}`
  - `title` → `={{ $('On form submission').item.json.URL.replace(/https?:\/\//, '').replace(/[^a-zA-Z0-9]+/g, '_') }}`

```js
{
  "markdown": {{ JSON.stringify($json.output) }},
  "title": {{ JSON.stringify('SEO Audit - ' + $('On form submission').item.json.URL.replace(/https?:\/\//, '').replace(/[^a-zA-Z0-9]+/g, '_')) }}
}
```

Then a **Convert to File** node (Operation: *Move Base64 String to File*, Base64 Input Field: `pdf_base64`, File Name: `={{ $json.filename }}`).

## Notes

- Uses [`markdown-pdf`](https://pypi.org/project/markdown-pdf/) (PyMuPDF under the hood). Pure-pip, no system libs.
- PyMuPDF is AGPL-3.0 — fine for personal/internal use, check before bundling into a closed-source product.
- Customize fonts/colors by editing `USER_CSS` in [server.py](server.py).
