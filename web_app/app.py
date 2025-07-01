from flask import Flask, render_template, request
import joblib
import re
import socket
import requests
from urllib.parse import urlparse
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from data_and_apis.external_api_fetcher import extract_features_from_apis
from ml_components.url_feature_extractor import URLFeatureExtractor
from datetime import datetime

app = Flask(__name__)

# Load mô hình với đường dẫn tuyệt đối
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(base_dir, "models", "model.pkl")
vectorizer_path = os.path.join(base_dir, "models", "vectorizer.pkl")

model = joblib.load(model_path)
vectorizer = joblib.load(vectorizer_path)

try:
    print("----------- Đang kiểm tra model...")
    dummy_vector = vectorizer.transform(["example.com/login"])
    model.predict(dummy_vector)
    print("----------- Model XGBoost hoạt động bình thường trên hệ thống Flask.")
except Exception as e:
    print("----------- Model gặp lỗi khi predict:")
    print(e)

# API keys
API_KEYS = {
    'google': 'AIzaSyCNfH__BftEQ-7hKmRY30vaMr8A8txTKb0',
    'virustotal': '6494720e47f1c51fc6051a033a970b8f7dddd7a1b6f34a9fa68f2bbddb8cec41',
    'ipinfo': '7a239af312eefc'
}

# Kiểm tra kết nối API
def test_api_connections():
    print("\n----------- Đang kiểm tra các API...")

    try:
        sb_url = "https://safebrowsing.googleapis.com/v4/threatMatches:find"
        sb_resp = requests.post(
            f"{sb_url}?key={API_KEYS['google']}",
            json={
                "client": {"clientId": "test", "clientVersion": "1.0"},
                "threatInfo": {
                    "threatTypes": ["MALWARE"],
                    "platformTypes": ["ANY_PLATFORM"],
                    "threatEntryTypes": ["URL"],
                    "threatEntries": [{"url": "http://example.com"}]
                }
            }
        )
        if sb_resp.status_code == 200:
            print("----------- Google Safe Browsing: OK")
        else:
            print("----------- Google Safe Browsing lỗi:", sb_resp.status_code)
    except Exception as e:
        print("----------- Google Safe Browsing exception:", e)

    try:
        wr_url = "https://webrisk.googleapis.com/v1/uris:search"
        wr_resp = requests.get(
            wr_url,
            params={
                "key": API_KEYS['google'],
                "uri": "http://example.com",
                "threatTypes": ["MALWARE"]
            }
        )
        if wr_resp.status_code == 200:
            print("----------- Google Web Risk: OK")
        else:
            print("----------- Google Web Risk lỗi:", wr_resp.status_code)
    except Exception as e:
        print("----------- Google Web Risk exception:", e)

    try:
        vt_url = "https://www.virustotal.com/api/v3/urls"
        vt_resp = requests.post(
            vt_url,
            headers={"x-apikey": API_KEYS['virustotal']},
            data={"url": "http://example.com"}
        )
        if vt_resp.status_code == 200:
            print("----------- VirusTotal: OK")
        else:
            print("----------- VirusTotal lỗi:", vt_resp.status_code)
    except Exception as e:
        print("----------- VirusTotal exception:", e)

    try:
        resp = requests.get(f"https://ipinfo.io/json?token={API_KEYS['ipinfo']}")
        if resp.status_code == 200:
            print("----------- IPInfo: OK")
        else:
            print("----------- IPInfo lỗi:", resp.status_code)
    except Exception as e:
        print("----------- IPInfo exception:", e)

# Các hàm xử lý URL
def normalize_url(url):
    return url if url.startswith("http") else "http://" + url

def strip_scheme_www(url):
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path or ""
    query = f"?{parsed.query}" if parsed.query else ""
    cleaned_url = (domain + path + query).rstrip('/')
    return cleaned_url.lower()


def check_domain_exists(url):
    try:
        hostname = urlparse(url).netloc or url
        socket.gethostbyname(hostname)
        return True
    except:
        return False

def calculate_risk_score(ai_prediction, api_features):
    score = 0
    sb = api_features.get("safe_browsing", 0)
    wr = api_features.get("web_risk", 0)
    vt = api_features.get("virustotal_malicious", 0)

    score += int(ai_prediction) * 4
    score += sb * 2
    score += wr * 2
    score += min(vt, 5)

    return min(score, 10)

# Inject thời gian vào template
@app.context_processor
def inject_now():
    return {'now': lambda: datetime.now().strftime("%I:%M %p, %d tháng %m, %Y")}

# Giao diện chính
@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    input_url = ""
    risk_score = None
    api_details = {}
    domain_status = None
    ai_score = None

    if request.method == "POST":
        input_url = request.form["url"].strip()
        input_url = normalize_url(input_url)
        processed_url = strip_scheme_www(input_url)

        domain_status = check_domain_exists(input_url)

        X_input = vectorizer.transform([processed_url])
        ai_pred = model.predict(X_input)[0]
        ai_score = int(ai_pred)

        api_details = extract_features_from_apis(input_url, API_KEYS)
        risk_score = calculate_risk_score(ai_pred, api_details)

        if risk_score >= 7:
            result = "NGUY HIỂM"
        elif risk_score >= 4:
            result = "NGHI NGỜ"
        else:
            result = "AN TOÀN"

        if not domain_status:
            result += " (Tên miền không phân giải được IP)"

    return render_template("index.html", url=input_url, prediction=result,
                           score=risk_score, api=api_details, domain_ok=domain_status,
                           ai_score=ai_score)

import os
if __name__ == "__main__":
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        test_api_connections()
    
    app.run(debug=True)
