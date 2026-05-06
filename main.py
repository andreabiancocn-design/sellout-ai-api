import base64
from fastapi import FastAPI, File, UploadFile
from analyzer import analyze_excel
from report_excel import create_excel_report
from report_pdf import create_pdf_report
from ai_report import generate_ai_report

app = FastAPI(title="Sellout AI API")

@app.get("/")
def health():
    return {"status": "ok", "message": "Sellout AI API attiva"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    file_bytes = await file.read()

    detail, summaries = analyze_excel(file_bytes)
    ai_text = generate_ai_report(summaries)

    excel_bytes = create_excel_report(detail, summaries, ai_text)
    pdf_bytes = create_pdf_report(ai_text)

    return {
        "filename": file.filename,
        "ai_report": ai_text,
        "excel_base64": base64.b64encode(excel_bytes).decode("utf-8"),
        "pdf_base64": base64.b64encode(pdf_bytes).decode("utf-8"),
    }
