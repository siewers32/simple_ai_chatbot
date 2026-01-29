
# Maak een virtuele omgeving (optioneel maar aanbevolen)
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

# Installeer de vereiste pakketten
pip install pandas openai python-dotenv tabulate
```

> `tabulate` maakt de weergave van data tabelair mooi.

---

## 2. .env‑bestand

Maak een bestand `.env` in dezelfde map als het script en voeg je OpenAI‑API‑sleutel toe:

```
OPENAI_API_KEY=sk-XXXXXXXXXXXXXXXXXXXXXXXX
```

> **Let op**: Bewaar het `.env`‑bestand niet in een publieke repository!

---

## 3. Het script (`csv_ai_bot.py`)

```python
#!/usr/bin/env python3
"""
csv_ai_bot.py

Stel een vraag aan een AI‑bot over een CSV‑bestand.
Het script leest het bestand, geeft een korte samenvatting
en stuurt jouw vraag via de OpenAI ChatCompletion API.
"""

import os
import sys
import pandas as pd
from tabulate import tabulate
import openai
from dotenv import load_dotenv

# ------------------------------------------------------------
# 1. Initialiseer OpenAI en laadt de API‑sleutel
# ------------------------------------------------------------
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")
if not openai.api_key:
    print("[❌] Geen OpenAI API‑sleutel gevonden. Voeg een .env toe.")
    sys.exit(1)

# ------------------------------------------------------------
# 2. CSV‑bestand inlezen
# ------------------------------------------------------------
def read_csv(path: str) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        print(f"[❌] Fout bij het inlezen van {path}: {e}")
        sys.exit(1)

# ------------------------------------------------------------
# 3. Genereren van een korte “prompt” over de data
# ------------------------------------------------------------
def generate_data_summary(df: pd.DataFrame) -> str:
    """Maak een korte beschrijving van de CSV‑inhoud."""
    # Beschrijving van kolomnamen en eerste 5 rijen
    header = ", ".join(df.columns.tolist())
    sample_rows = df.head(5).to_dict(orient="records")
    sample_text = "\n".join([f"{i+1}. {row}" for i, row in enumerate(sample_rows)])

    summary = (
        f"De CSV bevat {df.shape[0]} rijen en {len(df.columns)} kolommen.\n"
        f"Kolomnamen: {header}\n\n"
        f"Eerste 5 rijen:\n{sample_text}"
    )
    return summary

# ------------------------------------------------------------
# 4. AI‑vraag verwerken
# ------------------------------------------------------------
def ask_ai(question: str, data_summary: str) -> str:
    """Stuur de vraag en de datasection naar OpenAI."""
    system_prompt = (
        "Je bent een behulpzame data‑analist. Je krijgt "
        "een korte samenvatting van een CSV-bestand en vervolgens een vraag. "
        "Beantwoord de vraag zo nauwkeurig mogelijk, gebruik alleen informatie die in de samenvatting staat."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"Samenvatting van het CSV-bestand:\n\n{data_summary}\n\nVraag: {question}"},
    ]

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",  # of "gpt-3.5-turbo"
            messages=messages,
            temperature=0.2,  # minder creatief, meer feitelijk
            max_tokens=800,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"[❌] OpenAI‑fout: {e}")
        sys.exit(1)

# ------------------------------------------------------------
# 5. Interactieve CLI
# ------------------------------------------------------------
def main():
    if len(sys.argv) < 2:
        print("Gebruik: python csv_ai_bot.py <csv-bestand> [vraag]")
        sys.exit(0)

    csv_path = sys.argv[1]
    df = read_csv(csv_path)
    data_summary = generate_data_summary(df)

    # Als er een vraag in de commandoregel staat, gebruik die.
    if len(sys.argv) > 2:
        question = " ".join(sys.argv[2:])
    else:
        # Anders interactieve prompt
        print("\n=== AI‑Chatbot voor CSV ===")
        print(f"Bestand: {csv_path}\n")
        question = input("Stel je vraag (of druk op Enter om af te sluiten): ")
        if not question.strip():
            print("Geen vraag ingevoerd. Afsluiten.")
            sys.exit(0)

    answer = ask_ai(question, data_summary)
    print("\n--- AI‑antwoord ---")
    print(answer)

if __name__ == "__main__":
    main()
```

---

## 4. Gebruik

```bash
# Voorbeeld: stel een vraag over een CSV‑bestand
python csv_ai_bot.py data.csv "Hoeveel unieke waarden heeft kolom 'Product'?"
```

> **Resultaat**  
> Het script toont een korte samenvatting van de CSV en geeft vervolgens het antwoord op jouw vraag.

---

## 5. Uitbreidingen

| Idee | Hoe te implementeren |
|------|----------------------|
| **Meer context**: voeg volledige eerste 20 rijen toe aan de prompt. | Verhoog `df.head(20)` in `generate_data_summary`. |
| **Multiple choice**: laat de bot een lijst met opties geven. | Pas `system_prompt` aan om keuzes te genereren. |
| **Grafische weergave**: toon een plot van een kolom. | Gebruik `matplotlib` of `seaborn`. |
| **Batch‑verwerking**: leer meerdere vragen achter elkaar. | Loop over een lijst met prompts en stuur ze één voor één. |

---

## 6. Veelgemaakte fouten

| Fout | Oplossing |
|------|-----------|
| `openai.error.OpenAIError` vanwege quota‑limiet | Controleer je plan en API‑sleutel; gebruik `gpt-4o-mini` voor lagere kosten. |
| Onjuiste kolomnamen in de prompt | Gebruik `df.columns.tolist()` en controleer op spaties. |
| Taal‑problemen (vindt niet de juiste kolom) | Gebruik een duidelijke, taaldubbeling in het prompt: “Kolom 'Product'” vs. “product”. |

---