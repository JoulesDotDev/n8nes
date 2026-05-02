import base64, io
from fastapi import FastAPI
from pydantic import BaseModel
from markdown_pdf import MarkdownPdf, Section

app = FastAPI()

USER_CSS = """
h1 { border-bottom: 2px solid #333; padding-bottom: 4px; }
h1, h2, h3 { color: #111; }
code { background: #f3f3f3; padding: 1px 4px; border-radius: 3px; }
table { border-collapse: collapse; width: 100%; }
th, td { border: 1px solid #ddd; padding: 6px 8px; }
"""

class Req(BaseModel):
    markdown: str
    title: str | None = "Audit"

@app.post("/convert")
def convert(req: Req):
    pdf = MarkdownPdf(toc_level=2)
    pdf.meta["title"] = req.title
    pdf.add_section(Section(req.markdown), user_css=USER_CSS)
    buf = io.BytesIO()
    pdf.save(buf)
    return {
        "pdf_base64": base64.b64encode(buf.getvalue()).decode("ascii"),
        "filename": f"{req.title}.pdf",
    }