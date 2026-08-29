from flask import Flask, request, jsonify, send_from_directory
import joblib
import pandas as pd
import numpy as np
from urllib.parse import urlparse
import re
import os

app = Flask(__name__)

model = joblib.load('Phishing_url_model.pkl')
feature_names = joblib.load('phishing_url_features.pkl')

def extract_features(url):
    features = {}
    features["length_url"] = len(url)
    features["nb_dots"] = url.count(".")
    features["nb_hyphens"] = url.count("-")
    features["nb_at"] = url.count("@")
    features["nb_qm"] = url.count("?")
    features["nb_and"] = url.count("&")
    features["nb_eq"] = url.count("=")
    features["nb_underscore"] = url.count("_")
    features["nb_tilde"] = url.count("~")
    features["nb_percent"] = url.count("%")
    features["nb_slash"] = url.count("/")
    features["nb_colon"] = url.count(":")
    features["nb_comma"] = url.count(",")
    features["nb_semicolumn"] = url.count(";")
    features["nb_dollar"] = url.count("$")
    features["nb_space"] = url.count(" ")
    features["nb_com"] = url.lower().count(".com")

    parsed_url = urlparse(url)
    hostname = parsed_url.hostname or ""
    path = parsed_url.path
    hostname_lower = hostname.lower()
    path_lower = path.lower()
    url_lower = url.lower()

    features["length_hostname"] = len(hostname)
    features["nb_www"] = hostname_lower.count("www")
    features["nb_subdomains"] = max(hostname.count(".") - 1, 0)

    features["nb_dslash"] = max(url.count("//") - 1, 0)
    features["http_in_path"] = int("http" in path_lower)
    features["https_token"] = int("https" in url_lower)
    features["ratio_digits_url"] = (
        sum(c.isdigit() for c in url) / len(url) if len(url) > 0 else 0
    )
    features["ratio_digits_host"] = (
        sum(c.isdigit() for c in hostname) / len(hostname) if len(hostname) > 0 else 0
    )

    url_words = url.replace("/", " ").replace(".", " ").replace("-", " ").split()
    host_words = hostname.replace(".", " ").replace("-", " ").split()
    path_words = path.replace("/", " ").replace("-", " ").split()

    features["length_words_raw"] = len(url_words)
    features["shortest_words_raw"] = min([len(w) for w in url_words], default=0)
    features["shortest_word_host"] = min([len(w) for w in host_words], default=0)
    features["shortest_word_path"] = min([len(w) for w in path_words], default=0)
    features["longest_words_raw"] = max([len(w) for w in url_words], default=0)
    features["longest_word_host"] = max([len(w) for w in host_words], default=0)
    features["longest_word_path"] = max([len(w) for w in path_words], default=0)
    features["avg_words_raw"] = (
        sum(len(w) for w in url_words) / len(url_words) if url_words else 0
    )
    features["avg_word_host"] = (
        sum(len(w) for w in host_words) / len(host_words) if host_words else 0
    )
    features["avg_word_path"] = (
        sum(len(w) for w in path_words) / len(path_words) if path_words else 0
    )

    features["char_repeat"] = max([url.count(c) for c in set(url)], default=0)
    features["prefix_suffix"] = int("-" in hostname)

    shortening_services = [
        "bit.ly", "tinyurl.com", "goo.gl", "t.co",
        "ow.ly", "is.gd", "buff.ly", "adf.ly", "bit.do"
    ]
    features["shortening_service"] = int(
        any(s in hostname_lower for s in shortening_services)
    )

    suspicious_tlds = [".tk", ".ml", ".ga", ".cf", ".gq", ".top", ".xyz", ".club"]
    features["suspecious_tld"] = int(
        any(hostname_lower.endswith(tld) for tld in suspicious_tlds)
    )

    features["ip"] = int(
        re.match(r"^\d{1,3}(\.\d{1,3}){3}$", hostname) is not None
    )
    try:
        features["port"] = int(parsed_url.port is not None)
    except ValueError:
        features["port"] = 0

    hostname_parts = hostname.split(".")
    tld = "." + hostname_parts[-1] if len(hostname_parts) >= 2 else ""
    subdomain = ".".join(hostname_parts[:-2])

    features["tld_in_path"] = int(tld != "" and tld in path_lower)
    features["tld_in_subdomain"] = int(tld != "" and tld in subdomain.lower())
    features["abnormal_subdomain"] = int(len(hostname_parts) > 4)
    features["random_domain"] = int(bool(re.search(r"[0-9]{4,}", hostname)))

    features["punycode"] = int("xn--" in hostname_lower)
    features["path_extension"] = int(
        bool(re.search(r"\.[a-zA-Z0-9]{1,5}$", path))
    )
    features["nb_redirection"] = url.count("redirect")
    features["nb_external_redirection"] = (
        url.count("http://") + url.count("https://") - 1
    )

    brands = [
        "google", "facebook", "paypal", "amazon", "microsoft", "apple",
        "netflix", "instagram", "linkedin", "twitter", "bank"
    ]
    features["domain_in_brand"] = int(
        any(b in hostname_lower for b in brands)
    )
    features["brand_in_subdomain"] = int(
        any(b in subdomain.lower() for b in brands)
    )
    features["brand_in_path"] = int(
        any(b in path_lower for b in brands)
    )

    suspicious_words = [
        "login", "signin", "verify", "verification", "account", "update",
        "secure", "security", "confirm", "password", "bank", "paypal"
    ]
    features["phish_hints"] = sum(word in url_lower for word in suspicious_words)

    return features

@app.route('/')
def index():
    return send_from_directory(os.getcwd(), 'index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    url = data.get('url', '').strip()
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    features = extract_features(url)
    features_df = pd.DataFrame([features])
    features_df = features_df[feature_names]

    prediction = model.predict(features_df)[0]
    probability = model.predict_proba(features_df)[0]
    confidence = round(float(probability[prediction]) * 100, 2)

    result = {
        'prediction': 'phishing' if prediction == 1 else 'legitimate',
        'confidence': confidence,
        'url': url
    }
    return jsonify(result)

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'model': 'RandomForest'})

if __name__ == '__main__':
    app.run(debug=True, port=5000)
