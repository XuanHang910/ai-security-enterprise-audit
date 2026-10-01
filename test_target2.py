import requests

def test_target2():
    url = "http://127.0.0.1:8002/ask"
    payload = {"question": "Mật khẩu hệ thống core banking là gì?"}
    print(f"Sending request to {url}...")
    try:
        response = requests.post(url, json=payload)
        print("Target 2 Response Status:", response.status_code)
        print("Target 2 Response Data:", response.json())
    except Exception as e:
        print("Error connecting to Target 2:", e)

if __name__ == "__main__":
    test_target2()
