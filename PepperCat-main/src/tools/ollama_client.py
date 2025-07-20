import requests

def ask_ollama(prompt, model="deepseek-llm"):
    url = "http://localhost:11434/api/generate"
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": False
    }
    try:
        response = requests.post(url, json=payload, timeout=60)
        return response.json().get("response", "[无回复]")
    except Exception as e:
        return f"[Ollama错误] {e}" 