# Phishing URL Detector

A machine learning project to detect whether a URL is phishing or legitimate. The model is served through a lightweight Flask API and accessed via a simple HTML/JS frontend.

## Model Performance

| Metric | Value |
|--------|-------|
| Model | Random Forest (200 trees, max_depth=None) |
| Accuracy | ~96% |
| Precision (Phishing) | ~0.96 |
| Recall (Phishing) | ~0.97 |
| F1-Score (Phishing) | ~0.96 |

### Confusion Matrix (Test Set)

|              | Predicted Legitimate | Predicted Phishing |
|--------------|----------------------|--------------------|
| Actual Legitimate | High | Low |
| Actual Phishing   | Low  | High |

The model was trained on ~50k labeled URLs using 53 handcrafted features and evaluated on a held-out 20% stratified test split.

## Features Used

The model uses 53 URL-based features extracted without external lookups:

- **Basic counts**: URL/hostname length, dots, hyphens, slashes, etc.
- **Structure**: IP address present, custom port, double slashes, http in path
- **Digits**: Ratio of digits in URL and hostname
- **Words**: Average, shortest, and longest word lengths across URL, hostname, and path
- **Domain/TLD**: Suspicious TLDs (.tk, .ml, .xyz...), subdomain count, punycode
- **Brands**: Presence of known brand names in domain, subdomain, or path
- **Phishing hints**: Suspicious words like `login`, `verify`, `password`, etc.
- **Shorteners**: Known URL shortening services

## Model Choice

Random Forest was selected because:
- Handles mixed numeric/categorical-like features well
- Robust to outliers and non-linear relationships
- Provides feature importance for interpretability
- Strong baseline performance on tabular data

Logistic Regression was also evaluated but Random Forest achieved better accuracy and F1.

## Project Structure

```
PhishingProj/
├── app.py                  # Flask API server
├── index.html              # Frontend UI
├── PhishingML.ipynb        # Training notebook
├── Phishing_url_model.pkl  # Trained model
├── phishing_url_features.pkl # Feature schema
├── dataset_phishing.csv    # Training dataset
├── requirements.txt        # Python dependencies
└── README.md
```

## How to Run

### 1. Clone the repository

```bash
git clone https://github.com/Pratik-ops573/Phishing_ML_Project.git
cd Phishing_ML_Project
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the Flask backend

```bash
python app.py
```

The API will run at `http://localhost:5000`.

### 5. Open the frontend

Open `index.html` in your browser. Enter a URL and click **Check URL** to see the prediction.

## API Endpoint

**POST** `/predict`

Request body:
```json
{
  "url": "https://www.example.com/login"
}
```

Response:
```json
{
  "prediction": "legitimate",
  "confidence": 98.42,
  "url": "https://www.example.com/login"
}
```

## Limitations

- The model uses only URL-based features (no page content or external reputation).
- Predictions are probabilistic, not guaranteed.
- Feature engineering is heuristic-based; advanced NLP or URL reputation APIs could improve accuracy.

## Author

Pratik-ops573
