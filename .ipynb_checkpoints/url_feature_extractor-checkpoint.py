# url_feature_extractor.py
import re
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from tqdm import tqdm

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
        for url in tqdm(X, desc="Đang trích đặc trưng", disable=True):  
            features.append([
                len(url),
                url.count('.'),
                url.count('-'),
                int(bool(re.search(r'(\d{1,3}\.){3}\d{1,3}', url))),
                sum(1 for word in self.suspicious_keywords if word in url.lower())
            ])
        return np.array(features)
