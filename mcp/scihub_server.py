import sys
import json
import re
import httpx
import asyncio
from io import BytesIO

try:
    from pypdf import PdfReader
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False

MIRRORS = ["https://sci-hub.ru", "https://sci-hub.st", "https://sci-hub.ee", "https://sci-hub.se"]

def respond(data):
    sys.stdout.write(json.dumps(data) + "\n")
    sys.stdout.flush()

async def try_fetch(doi: str) -> dict:
    for mirror in MIRRORS:
        url = f"{mirror}/{doi}"
        try:
            async with httpx.AsyncClient(timeout=15.0, follow_redirects=True) as c:
                r = await c.get(url, headers={"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"})
                ctype = r.headers.get("content-type", "")
                if "pdf" in ctype:
                    text = "PDF retrieved."
                    if PDF_SUPPORT:
                        try:
                            pdf = PdfReader(BytesIO(r.content))
                            text = "\n".join(p.extract_text() for p in pdf.pages[:15])
                        except Exception:
                            text = "PDF retrieved but text extraction failed."
                    return {"success": True, "text": text[:4000]}
                html = r.text
                # Cerca embed PDF
                m = re.search(r'embed[^>]+src=["\']([^"\']+\.pdf[^"\']*)', html, re.I)
                if m:
                    pdf_url = m.group(1)
                    if pdf_url.startswith("//"):
                        pdf_url = "https:" + pdf_url
                    r2 = await c.get(pdf_url)
                    text = "PDF retrieved via embed."
                    if PDF_SUPPORT:
                        try:
                            pdf = PdfReader(BytesIO(r2.content))
                            text = "\n".join(p.extract_text() for p in pdf.pages[:15])
                        except Exception:
                            pass
                    return {"success": True, "text": text[:4000]}
                # Fallback: estrai testo dall'HTML
                clean = re.sub(r'<[^>]+>', '', html)
                clean = re.sub(r'\s+', ' ', clean).strip()[:3000]
                return {"success": True, "text": clean}
        except Exception as e:
            continue
    return {"success": False, "text": f"Sci-Hub non raggiungibile su nessun mirror"}

def handle_request(req):
    method = req.get("method", "")
    rid = req.get("id")
    if method == "initialize":
        respond({"jsonrpc": "2.0", "id": rid, "result": {
            "protocolVersion": "2024-11-05",
            "serverInfo": {"name": "scihub-mcp", "version": "0.1.0"},
            "capabilities": {"tools": {}},
        }})
    elif method == "tools/list":
        respond({"jsonrpc": "2.0", "id": rid, "result": {"tools": [{
            "name": "fetch_paper",
            "description": "Fetch a scientific paper from Sci-Hub by DOI",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "doi": {"type": "string", "description": "DOI (e.g. 10.1000/xyz123)"},
                },
                "required": ["doi"],
            }
        }]}})
    elif method == "tools/call":
        params = req.get("params", {})
        name = params.get("name", "")
        args = params.get("arguments", {})
        if name == "fetch_paper":
            doi = args.get("doi", "").strip()
            if not doi:
                respond({"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": "DOI required"}})
                return
            result = asyncio.run(try_fetch(doi))
            if result["success"]:
                respond({"jsonrpc": "2.0", "id": rid, "result": {
                    "content": [{"type": "text", "text": f"Paper (DOI: {doi}):\n{result['text'][:4000]}"}]
                }})
            else:
                respond({"jsonrpc": "2.0", "id": rid, "error": {"code": -32000, "message": result["text"]}})
        else:
            respond({"jsonrpc": "2.0", "id": rid, "error": {"code": -32602, "message": f"Tool {name} not found"}})
    elif method == "notifications/initialized":
        pass
    else:
        respond({"jsonrpc": "2.0", "id": rid, "error": {"code": -32601, "message": f"Method {method} not found"}})

if __name__ == "__main__":
    for line in sys.stdin:
        try:
            req = json.loads(line.strip())
            handle_request(req)
        except json.JSONDecodeError:
            continue
        except SystemExit:
            break
