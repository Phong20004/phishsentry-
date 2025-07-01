import requests
import socket
from urllib.parse import urlparse

def extract_domain(url):
    try:
        parsed = urlparse(url if url.startswith("http") else "http://" + url)
        return parsed.netloc
    except:
        return ""

def check_safe_browsing(url, api_key):
    endpoint = f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={api_key}"
    body = {
        "client": {"clientId": "phishing-ai", "clientVersion": "1.0"},
        "threatInfo": {
            "threatTypes": ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"],
            "platformTypes": ["ANY_PLATFORM"],
            "threatEntryTypes": ["URL"],
            "threatEntries": [{"url": url}]
        }
    }
    try:
        response = requests.post(endpoint, json=body)
        if response.status_code == 200 and response.json().get("matches"):
            return 1
    except Exception as e:
        print("Safe Browsing Error:", e)
    return 0

def check_web_risk(url, api_key):
    endpoint = "https://webrisk.googleapis.com/v1/uris:search"
    threat_types = ["MALWARE", "SOCIAL_ENGINEERING", "UNWANTED_SOFTWARE"]

    threat_count = 0
    for t in threat_types:
        try:
            response = requests.get(endpoint, params={
                "key": api_key,
                "uri": url,
                "threatTypes": [t]
            })
            if response.status_code == 200:
                data = response.json()
                if "threat" in data:
                    threat_count += 1
        except Exception as e:
            print(f"Web Risk Error ({t}):", e)

    return threat_count

import requests
import time
import base64

def check_virustotal(url, api_key):
    headers = {"x-apikey": api_key}

    try:
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        if response.status_code == 200:
            data = response.json()
            malicious_count = data['data']['attributes']['last_analysis_stats'].get('malicious', 0)
            return malicious_count
        else:
            print("----------- VT /urls/{id} lỗi:", response.status_code)
    except Exception as e:
        print("----------- VirusTotal exception:", e)

    return 0

def check_ipinfo(domain, token):
    try:
        ip = socket.gethostbyname(domain)
        response = requests.get(f"https://ipinfo.io/{ip}?token={token}")
        if response.status_code == 200:
            data = response.json()
            return {
                "country": data.get("country", ""),
                "org": data.get("org", ""),
                "asn": data.get("asn", {}).get("asn", "")
            }
    except Exception as e:
        print("IPInfo Error:", e)
    return {}

def extract_features_from_apis(url, keys):
    domain = extract_domain(url)
    return {
        "safe_browsing": check_safe_browsing(url, keys['google']),
        "web_risk": check_web_risk(url, keys['google']),
        "virustotal_malicious": check_virustotal(url, keys['virustotal']),
        "ipinfo": check_ipinfo(domain, keys['ipinfo'])
    }
