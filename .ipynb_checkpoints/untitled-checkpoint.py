import requests

api_key = "AIzaSyCNfH__BftEQ-7hKmRY30vaMr8A8txTKb0"
url = "http://testsafebrowsing.appspot.com/s/malware.html"

endpoint = "https://webrisk.googleapis.com/v1/uris:search"

# Lặp từng threatType như Google yêu cầu
threat_types = ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"]

for threat_type in threat_types:
    params = {
        "key": api_key,
        "uri": url,
        "threatTypes": threat_type
    }

    print(f"\n🔎 Kiểm tra với threatType: {threat_type}")
    response = requests.get(endpoint, params=params)

    print("📡 Status code:", response.status_code)
    try:
        result = response.json()
        if "threat" in result:
            print("⚠️ Phát hiện mối đe dọa:")
            print(result)
        else:
            print("✅ Không phát hiện mối đe dọa.")
    except requests.exceptions.JSONDecodeError:
        print("❌ Không đọc được JSON.")
        print(response.text)
