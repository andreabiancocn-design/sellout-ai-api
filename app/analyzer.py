import io
import pandas as pd

TYPE_MAP = {
    "0-Acquisito": "acquisito",
    "1-Venduto": "venduto",
    "2-Esistenza": "esistenza",
}

BASE_COLS = ["negozio", "modello", "stagione", "brand", "gruppo", "settore", "ignore", "tipo"]

def _clean_col(value):
    if pd.isna(value):
        return ""
    return str(value).strip()


def analyze_excel(file_bytes: bytes):
    # Riga 5 come intestazione: pandas usa header=4 perché l'indice parte da 0.
    df = pd.read_excel(io.BytesIO(file_bytes), header=4)
    df = df.dropna(how="all")

    # Rinomina prime 8 colonne secondo la struttura concordata.
    original_cols = list(df.columns)
    rename_map = {original_cols[i]: BASE_COLS[i] for i in range(min(8, len(original_cols)))}
    df = df.rename(columns=rename_map)

    # Tiene solo righe con tipo dato valido.
    df["tipo"] = df["tipo"].astype(str).str.strip()
    df = df[df["tipo"].isin(TYPE_MAP.keys())].copy()
    df["tipo_norm"] = df["tipo"].map(TYPE_MAP)

    # Colonne taglie: dalla I in poi, cioè dopo le prime 8 colonne.
    size_cols = list(df.columns[8:])
    size_cols = [c for c in size_cols if str(c).strip() and not str(c).startswith("Unnamed")]

    # Da formato largo a formato lungo: una riga per ogni taglia.
    melted = df.melt(
        id_vars=["negozio", "modello", "stagione", "brand", "gruppo", "settore", "tipo_norm"],
        value_vars=size_cols,
        var_name="taglia",
        value_name="quantita",
    )
    melted["taglia"] = melted["taglia"].map(_clean_col)
    melted["quantita"] = pd.to_numeric(melted["quantita"], errors="coerce").fillna(0)

    pivot = melted.pivot_table(
        index=["negozio", "modello", "stagione", "brand", "gruppo", "settore", "taglia"],
        columns="tipo_norm",
        values="quantita",
        aggfunc="sum",
        fill_value=0,
    ).reset_index()

    for col in ["acquisito", "venduto", "esistenza"]:
        if col not in pivot.columns:
            pivot[col] = 0

    pivot["sellout_pct"] = pivot.apply(
        lambda r: (r["venduto"] / r["acquisito"] * 100) if r["acquisito"] else 0,
        axis=1,
    ).round(2)

    summary_keys = {
        "brand": ["brand"],
        "gruppo": ["brand", "gruppo"],
        "modello": ["brand", "gruppo", "settore", "modello"],
        "taglia": ["brand", "gruppo", "settore", "taglia"],
        "negozio": ["negozio", "brand", "gruppo"],
    }

    summaries = {}
    for name, keys in summary_keys.items():
        s = pivot.groupby(keys, dropna=False)[["acquisito", "venduto", "esistenza"]].sum().reset_index()
        s["sellout_pct"] = s.apply(
            lambda r: (r["venduto"] / r["acquisito"] * 100) if r["acquisito"] else 0,
            axis=1,
        ).round(2)
        summaries[name] = s.sort_values(["sellout_pct", "venduto"], ascending=False)

    return pivot, summaries
