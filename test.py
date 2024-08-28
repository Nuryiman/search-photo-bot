import requests

try:
    response = requests.get("https://www.bing.com")
    if response.status_code == 200:
        print("Доступ к Bing есть.")
    else:
        print("Доступ к Bing ограничен.")
except Exception as e:
    print(f"Ошибка при подключении к Bing: {e}")
