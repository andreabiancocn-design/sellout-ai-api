import io
import pandas as pd


def create_excel_report(detail, summaries, ai_text):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        detail.to_excel(writer, index=False, sheet_name="Dettaglio normalizzato")
        for name, df in summaries.items():
            df.to_excel(writer, index=False, sheet_name=name[:31])
        pd.DataFrame({"Report AI": [ai_text]}).to_excel(writer, index=False, sheet_name="AI Report")
    output.seek(0)
    return output.getvalue()
