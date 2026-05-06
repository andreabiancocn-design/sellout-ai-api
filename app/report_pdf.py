import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


def create_pdf_report(ai_text):
    output = io.BytesIO()
    doc = SimpleDocTemplate(output, pagesize=A4)
    styles = getSampleStyleSheet()
    story = [Paragraph("Report Sellout AI", styles["Title"]), Spacer(1, 12)]
    for paragraph in ai_text.split("\n"):
        if paragraph.strip():
            story.append(Paragraph(paragraph.strip(), styles["BodyText"]))
            story.append(Spacer(1, 8))
    doc.build(story)
    output.seek(0)
    return output.getvalue()
