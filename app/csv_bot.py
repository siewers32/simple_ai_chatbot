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

client = openai.OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), # Soms vereist je eigen server dit niet, maar vul iets in
    base_url="http://10.41.50.130:1234/v1/" 
)

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
    # Beschrijving van kolomnamen en eerste 20 rijen
    header = ", ".join(df.columns.tolist())
    sample_rows = df.head(20).to_dict(orient="records")
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
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b", 
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