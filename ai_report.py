import os
from openai import OpenAI


def build_ai_prompt(summaries):
    top_modelli = summaries["modello"].head(20).to_dict(orient="records")
    top_taglie = summaries["taglia"].head(20).to_dict(orient="records")
    top_negozi = summaries["negozio"].head(20).to_dict(orient="records")

    return f"""
Sei un analista retail moda. Analizza questi dati sellout e scrivi un report operativo in italiano.
Obiettivo: aiutare buyer e azienda a creare nuovi campionari.

Devi produrre:
1. Sintesi generale
2. Modelli da riproporre
3. Taglie da rafforzare
4. Brand/gruppi più performanti
5. Negozi migliori e peggiori
6. Prodotti o aree critiche
7. Raccomandazioni pratiche per il prossimo campionario

Top modelli:
{top_modelli}

Top taglie:
{top_taglie}

Top negozi:
{top_negozi}
"""


def generate_ai_report(summaries):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return "AI non configurata: aggiungere OPENAI_API_KEY nelle variabili ambiente di Render."

    client = OpenAI(api_key=api_key)
    prompt = build_ai_prompt(summaries)

    response = client.chat.completions.create(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        messages=[
            {"role": "system", "content": "Rispondi come consulente retail esperto, in modo pratico e sintetico."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message.content
