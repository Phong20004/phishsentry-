import pandas as pd
import numpy as np
import re
from urllib.parse import urlparse
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
from sklearn.pipeline import FeatureUnion
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.base import BaseEstimator, TransformerMixin
from xgboost import XGBClassifier
import joblib
from tqdm import tqdm

def normalize_url(url):
    return url if url.startswith("http") else "http://" + url

def strip_scheme_www(url):
    url = normalize_url(url)
    parsed = urlparse(url)
    domain = parsed.netloc.replace("www.", "")
    path = parsed.path or ""
    query = f"?{parsed.query}" if parsed.query else ""
    return domain + path + query

class URLFeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.suspicious_keywords = [
            'login', 'secure', 'update', 'verify', 'account', 'bank', 'signin', 'submit',
            'paypal', 'ebay', 'confirm', 'wp', 'mail', 'admin', '88', '365', 'bet', '68', '86'
        ]

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        features = []
        for url in tqdm(X, desc="Đang trích đặc trưng"):
            features.append([
                len(url),
                url.count('.'),
                url.count('-'),
                int(bool(re.search(r'(\d{1,3}\.){3}\d{1,3}', url))),
                sum(1 for word in self.suspicious_keywords if word in url.lower())
            ])
        return np.array(features)

def load_datasets():
    print("Đang tải và gộp dữ liệu...")
    df1 = pd.read_csv("../data_and_apis/datasets/openphish.csv")[['url']].assign(label=1)
    df2 = pd.read_csv("../data_and_apis/datasets/urlhaus.csv")[['url']].assign(label=1)
    df3 = pd.read_csv("../data_and_apis/datasets/phishtank.csv")[['url']].assign(label=1)

    df4 = pd.read_csv("../data_and_apis/datasets/legit.csv", header=None, names=["index", "domain"])
    df4['url'] = "http://" + df4['domain'].astype(str)
    df4 = df4[['url']].assign(label=0)

    df_phish = pd.concat([df1, df2, df3], ignore_index=True).drop_duplicates(subset='url')
    df_legit = df4.drop_duplicates(subset='url')

    min_len = min(len(df_phish), len(df_legit))
    df_phish = df_phish.sample(n=min_len, random_state=42)
    df_legit = df_legit.sample(n=min_len, random_state=42)

    print(f"Dữ liệu sau cân bằng: {len(df_phish)} lừa đảo, {len(df_legit)} hợp lệ")

    df = pd.concat([df_phish, df_legit], ignore_index=True)
    df['url'] = df['url'].astype(str).apply(strip_scheme_www)
    return df

def train_model():
    df = load_datasets()
    X = df['url']
    y = df['label']

    print("Trích xuất đặc trưng...")
    vectorizer = TfidfVectorizer(analyzer='char_wb', ngram_range=(3, 5), max_features=5000)
    feature_union = FeatureUnion([
        ('tfidf', vectorizer),
        ('custom', URLFeatureExtractor())
    ])
    X_features = feature_union.fit_transform(X)

    print("Chia tập train/test...")
    X_train, X_test, y_train, y_test = train_test_split(X_features, y, test_size=0.2, random_state=42)

    print("Huấn luyện mô hình XGBoost...")
    model = XGBClassifier(
        tree_method='hist',
        max_depth=30,
        n_estimators=200,
        use_label_encoder=False,
        eval_metric='logloss',
        verbosity=1
    )
    model.fit(X_train, y_train)

    print("Đánh giá mô hình:")
    y_pred = model.predict(X_test)
    print("\nAccuracy:", accuracy_score(y_test, y_pred))
    print(classification_report(y_test, y_pred))

    print("Đang lưu model...")
    joblib.dump(model, '../models/model.pkl')
    joblib.dump(feature_union, '../models/vectorizer.pkl')
    print("Đã lưu ../models/model.pkl và ../models/vectorizer.pkl")

if __name__ == "__main__":
    train_model()
