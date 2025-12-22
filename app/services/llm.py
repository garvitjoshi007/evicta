import requests

LLM_URL = "http://localhost:11434/api/generate"

def generate_response(prompt: str) -> str:
    payload = {
        "model": "gemma:2b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(LLM_URL, json=payload)
    data = response.json()
    return data["response"]

# print(generate_response("Why is the sky blue?"))
