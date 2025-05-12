import requests

def find_similar_answer(user_question):
    url = "https://similarity-0dbg.onrender.com"
    data = {"data": [user_question]}
    try:
        response = requests.post(url, json=data, timeout=10)  # 10 second timeout
        if response.status_code == 200:
            response_data = response.json()
            answer = response_data.get('data', [None])[0]
            if answer:
                return answer
    except requests.Timeout:
        return None  # Timeout, fallback to OpenAI
    except Exception:
        return None