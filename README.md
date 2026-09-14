# 🛡️ Phishing URL Detector

A machine learning-powered web application that detects phishing URLs with ~96.3% accuracy using a trained Random Forest classifier and comprehensive feature extraction (URL structure, HTML content, WHOIS, DNS).

**Try it online:** [Deploy on Streamlit Community Cloud](#deployment)

## Model Performance

| Metric | Value |
|--------|-------|
| Model | Random Forest (100 trees) |
| Accuracy | ~96.3% |
| Precision (Phishing) | ~96% |
| Recall (Phishing) | ~97% |
| F1-Score (Phishing) | ~96% |
| Test Set Size | 20% (~10k URLs) |

The model was trained on ~50k labeled URLs using 80 handcrafted features and evaluated on a held-out 20% stratified test split.

---

## Features Extracted (80 Total)

### 1. URL-Level Features (~45)
- **Basic Counts**: length, dots, hyphens, slashes, colons, underscores, special chars
- **Structure**: IP detection, port presence, protocol scheme, double slashes
- **Ratios**: digit ratio in URL/hostname, word statistics
- **Hostname**: length, subdomain count, www presence, TLD info
- **Phishing Hints**: suspicious words (login, verify, password, bank, etc.)
- **Shorteners**: detection of bit.ly, tinyurl, goo.gl, etc.
- **Suspicious TLDs**: .tk, .ml, .ga, .cf, .gq, .top, .xyz, .club
- **Brands**: presence of known brands (Google, Facebook, PayPal, Amazon, etc.)

### 2. HTML/Page-Content Features (~19)
- **Hyperlinks**: count, internal vs external ratio
- **Forms**: login form detection (password input)
- **Media**: external CSS, images, videos, iframes
- **Scripts**: popup detection, onmouseover events, right-click handlers
- **Title**: empty title, domain in title
- **Meta**: redirects, favicon source (external vs internal)

### 3. Domain/WHOIS Features (~3)
- **Registered Domain**: WHOIS record exists (0/1)
- **Domain Age**: days since registration (or -1 if unknown)
- **Registration Length**: days until expiration (or -1 if unknown)

### 4. DNS Features (~1)
- **DNS Record**: A record resolves (0/1)

### 5. Traffic/Ranking Features (~4)
- **Web Traffic, Page Rank, Google Index, Statistical Report**: Approximated with neutral defaults (0)
- *Note: Free tier limitation. These historical Alexa-based signals are now approximated.*

---

## Project Structure

```
PhishingProj/
├── streamlit_app.py              # Streamlit web app (main)
├── feature_extraction.py         # Feature extraction module
├── PhishingML.ipynb              # Training notebook
├── Phishing_url_model.pkl        # Trained Random Forest model
├── phishing_url_features.pkl     # Feature names (column order)
├── dataset_phishing.csv          # Training dataset (~50k URLs)
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.8+
- Git

### Installation & Running

```bash
# 1. Clone the repository
git clone <repo-url>
cd PhishingProj

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate     # Windows
source venv/bin/activate  # macOS/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Streamlit app
streamlit run streamlit_app.py
```

The app will open at `http://localhost:8501` in your default browser.

### What to Expect
- Enter a URL (e.g., `https://www.google.com` or just `amazon.com`)
- Click **Check URL**
- Get verdict: ✅ **Legitimate** or ⚠️ **Phishing** with confidence %
- View all 80 extracted features in an expandable section
- See note if page fetch failed (prediction based on URL only)

---

## 🌐 Deployment to Streamlit Community Cloud

### Step 1: Push Code to GitHub

```bash
# If not already a git repo
git init
git add .
git commit -m "Add Streamlit phishing detector"
git remote add origin https://github.com/<your-username>/<your-repo>.git
git push -u origin main
```

### Step 2: Deploy via Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your GitHub repo, branch, and main file:
   - **Repository**: `<your-username>/<your-repo>`
   - **Branch**: `main`
   - **Main file path**: `streamlit_app.py`
4. Click **"Deploy!"**

Streamlit will install dependencies from `requirements.txt` and launch your app.

### Step 3: Share Your Link

Once deployed, you'll get a public link like:
```
https://phishing-detector-abc123.streamlit.app
```

Share this link with anyone to let them check URLs!

---

## 📋 Feature Extraction Details

### URL-Level Features
No external network calls required. Purely algorithmic parsing of the URL string:
- Character/word counts, ratios, patterns
- IP address and port detection via regex
- Brand and suspicious keyword matching

### HTML/Page-Content Features
Optional page fetch (5-second timeout) to analyze DOM:
- Counts of `<a>`, `<form>`, `<img>`, `<iframe>`, `<script>` elements
- Login form detection (password input)
- Favicon source (internal vs external)
- Link anchor text analysis
- Error handling: if page fetch fails, these features default to 0 and a warning is shown

### WHOIS Features
Uses `python-whois` to query domain registration:
- Domain age (days since creation)
- Registration length (days until expiration)
- Registered indicator (0/1)
- Gracefully handles rate-limiting; defaults to -1 (unknown) on failure

### DNS Features
Uses `dnspython` to check A record resolution:
- Returns 1 if domain resolves, 0 otherwise
- 3-second timeout per lookup

### Traffic/Ranking Features
Approximated with neutral defaults (0) due to free-tier limitations:
- Alexa traffic rank (defunct)
- Google PageRank (deprecated)
- Google index presence
- Statistical reports
- These are placeholders; consider paid APIs for production

---

## 🔒 Privacy & Security

- **No data logging**: URLs are not stored on the server
- **No external tracking**: App does not collect usage stats
- **API calls only when needed**: Page fetch, WHOIS, DNS are made only for the submitted URL
- **HTTPS on Streamlit Cloud**: Secure connection by default
- **User discretion advised**: Always verify unfamiliar links independently

---

## 🛠️ Training & Model Details

See [PhishingML.ipynb](PhishingML.ipynb) for:
- Data loading and EDA
- Feature extraction logic
- Model training (Logistic Regression vs Random Forest comparison)
- Hyperparameter tuning (GridSearchCV)
- Model evaluation and confusion matrix
- Feature importance analysis
- Artifact serialization (joblib.dump)

### Training Dataset
- **Size**: ~50k URLs
- **Classes**: Legitimate (0) and Phishing (1)
- **Train/Test**: 80/20 split with stratification
- **Source**: Public phishing datasets

---

## ⚠️ Disclaimer

This tool is a **machine learning heuristic** and should not be your sole trust indicator. 

**Always:**
- Verify links independently before clicking
- Check email sender and domain carefully
- Never enter credentials on unfamiliar pages
- Use browser security extensions (uBlock Origin, HTTPS Everywhere)
- Keep your OS and browser updated

**This app helps**, but responsible internet hygiene is still essential.

---

## 📝 License

[MIT License](LICENSE) – feel free to use, modify, and distribute.

---

## 🤝 Contributing

Contributions welcome! To improve this project:
1. Fork the repo
2. Create a feature branch (`git checkout -b feature/my-improvement`)
3. Commit changes (`git commit -am 'Add feature'`)
4. Push (`git push origin feature/my-improvement`)
5. Open a Pull Request

---

## 💬 Questions?

Open an issue on GitHub or reach out via [your contact info].
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
