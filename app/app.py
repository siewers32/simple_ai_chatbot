from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

# 1. Initialiseer de client met je API-sleutel
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"), # Soms vereist je eigen server dit niet, maar vul iets in
    base_url="http://10.41.50.130:1234/v1/" 
)
# 2. Start het geheugen van de chatbot
messages = [
    {"role": "system", "content": "Je bent een behulpzame assistent."}
]

print("Chatbot actief! Typ 'stop' om te sluiten.")

while True:
    # 3. Input van de gebruiker
    user_input = input("Jij: ")
    
    if user_input.lower() == "stop":
        break

    # Voeg de vraag van de gebruiker toe aan het geheugen
    messages.append({"role": "user", "content": user_input})

    # 4. Roep de OpenAI API aan
    response = client.chat.completions.create(
        model="openai/qwen3-4b-mlx", 
        messages=messages
    )

    # 5. Toon het antwoord en sla het op in het geheugen
    chat_answer = response.choices[0].message.content
    print(f"Bot: {chat_answer}")
    messages.append({"role": "assistant", "content": chat_answer})
