# 🔒 Hệ Thống Phát Hiện URL Lừa Đảo

Một ứng dụng web sử dụng Machine Learning (XGBoost) và các API bên ngoài để phân tích và phát hiện các URL lừa đảo (phishing) trong thời gian thực.

## ✨ Tính Năng Chính

- **Phân Tích AI**: Sử dụng mô hình XGBoost **pre-trained từ Kaggle** để dự đoán mức độ nguy hiểm.
- **Tích Hợp API**: Tăng cường độ chính xác bằng cách kiểm tra URL qua Google Safe Browsing và VirusTotal.
- **Trích Xuất Đặc Trưng**: Phân tích các đặc điểm của URL như độ dài, từ khóa đáng ngờ, và sự hiện diện của IP.
- **Giao Diện Trực Quan**: Giao diện web đơn giản, hiển thị kết quả phân tích và điểm rủi ro.

## ☁️ Workflow Huấn Luyện (Kaggle)

Mô hình Machine Learning của dự án được huấn luyện trên nền tảng **Kaggle Notebooks** để tận dụng tài nguyên mạnh mẽ và quản lý dữ liệu hiệu quả.

- **File `train_model.py`** trong project này chỉ mang tính chất **minh họa** cho quy trình huấn luyện.
- **Các file `model.pkl` và `vectorizer.pkl`** trong thư mục `/models` là các mô hình đã được huấn luyện sẵn và tải về từ Kaggle để sử dụng trong ứng dụng web.

## 🛠️ Công Nghệ Sử Dụng

- **Backend**: Flask (Python)
- **Machine Learning**: Scikit-learn, XGBoost, Pandas
- **Frontend**: HTML, CSS, Bootstrap 5
- **Training Environment**: Kaggle Notebooks

## 📁 Cấu Trúc Thư Mục

```
📁 CDCS/
├── 🧠 ml_components/              # AI/ML Components
│   ├── train_model.py            # (Script minh họa huấn luyện)
│   └── url_feature_extractor.py  # Trích xuất 5 đặc trưng từ URL
│
├── 🗃️ models/                     # (Mô hình pre-trained từ Kaggle)
│   ├── model.pkl                 # Mô hình XGBoost đã train
│   └── vectorizer.pkl            # FeatureUnion (TF-IDF + Custom)
│
├── 🌐 web_app/                    # Flask Web Application
│   ├── app.py                    # Flask server + API integration
│   ├── templates/
│   │   └── index.html            # Bootstrap 5.3.0 UI
│   └── static/
│       └── icons/                # Status icons (safe/warning/danger)
│
├── 📊 data_and_apis/             # Data & External APIs
│   ├── external_api_fetcher.py   # Google/VirusTotal/IPInfo APIs
│   └── datasets/                 # Training datasets
│
├── 📓 notebooks/                 # Jupyter Notebooks (Kaggle)
└── 🔄 .ipynb_checkpoints/        # Kaggle backup files (**CẦN THIẾT**)
```

## 🚀 Cài Đặt và Khởi Chạy

**Yêu cầu**: Python 3.8+

1.  **Clone a repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-folder>
    ```

2.  **Tạo môi trường ảo (khuyến khích):**
    ```bash
    python -m venv .venv
    .venv\Scripts\activate # Windows
    ```

3.  **Cài đặt các thư viện cần thiết:**
    ```bash
    pip install flask xgboost scikit-learn pandas numpy requests joblib tqdm
    ```

4.  **Chạy ứng dụng (sử dụng model đã train sẵn):**
    ```bash
    python web_app/app.py
    ```

5.  **Truy cập ứng dụng:**
    Mở trình duyệt và truy cập `http://localhost:5000`.

## 📈 Luồng Hoạt Động

1.  **Người dùng** nhập URL vào giao diện web.
2.  **Flask Server** nhận URL và gửi đến các module phân tích.
3.  **Module AI** (sử dụng model từ Kaggle) và **Module API** chạy song song.
4.  **Điểm Rủi Ro** được tính toán dựa trên kết quả từ AI và API.
5.  **Kết quả** (An toàn, Nghi ngờ, Nguy hiểm) được trả về và hiển thị cho người dùng.
