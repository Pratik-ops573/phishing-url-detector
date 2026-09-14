# ⚡ Quick Reference: Phishing Detector Commands

## 🏃 Local Setup (Copy & Paste)

```bash
# 1. Navigate to project
cd c:\Users\ASUS\Desktop\PhishingProj

# 2. Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the app
streamlit run streamlit_app.py

# Browser opens automatically at http://localhost:8501
```

---

## 🧪 Test the App

```bash
# Run validation tests
python test_app.py

# Test URLs to try:
# - Legitimate: https://www.google.com
# - Legitimate: amazon.com
# - Phishing: paypal-verify-account.tk/login
# - Phishing: google-update-password.xyz/verify
```

---

## 🚀 Deploy to Streamlit Cloud

```bash
# 1. Push to GitHub
git init
git add .
git commit -m "Add Streamlit phishing detector"
git branch -M main
git remote add origin https://github.com/<USERNAME>/<REPO>.git
git push -u origin main

# 2. Go to share.streamlit.io
#    - Click "New app"
#    - Select your repo, main branch
#    - Main file: streamlit_app.py
#    - Click "Deploy!"

# 3. Share the generated link (https://phishing-detector-xyz.streamlit.app)
```

---

## 📁 File Structure

| File | Purpose |
|------|---------|
| `streamlit_app.py` | Main web app (run this) |
| `feature_extraction.py` | 80-feature extraction logic |
| `Phishing_url_model.pkl` | Trained model (required) |
| `phishing_url_features.pkl` | Feature names (required) |
| `requirements.txt` | Package list for pip |
| `test_app.py` | Validation script |
| `README.md` | Full documentation |
| `DEPLOYMENT_GUIDE.md` | Detailed deployment steps |
| `PhishingML.ipynb` | Training notebook (reference) |

---

## 🔧 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: streamlit` | `pip install streamlit==1.28.1` |
| `.pkl` files not found | Ensure they're in the working directory |
| Slow page fetch | Some servers block requests; app continues gracefully |
| Streamlit slow on Cloud | First deployment builds packages (~2-3 min) |
| URL entry errors | App validates input and shows helpful messages |

---

## 📊 Model Info

- **Accuracy**: 96.3%
- **Features**: 80 (URL + HTML + WHOIS + DNS + Traffic)
- **Training Data**: ~50k URLs
- **Model Type**: Random Forest (100 trees)
- **Prediction Time**: <100ms

---

## 🔒 Privacy

✅ No data logging  
✅ No third-party tracking  
✅ All processing on your machine (or Streamlit's servers)  
✅ Predictions not stored between sessions  

---

## 💡 Pro Tips

1. **Local testing first** → Test locally before pushing to Cloud
2. **Check internet** → Page fetch and WHOIS lookups need network
3. **Share the link** → Streamlit Cloud provides public URL
4. **Bookmark it** → Keep the link handy for daily phishing checks
5. **Read sidebar** → App shows accuracy/disclaimer in sidebar

---

## 📱 Example Usage

**User enters:** `paypal-verify-account.xyz/login`

**App does:**
1. Extracts 80 features (URL + HTML + WHOIS + DNS)
2. Builds feature vector
3. Runs RandomForest prediction
4. Shows: ⚠️ **90% Phishing** (red badge)
5. Displays all extracted features in expandable table
6. Warns if page fetch failed

**Time**: 3-8 seconds (shown with spinner)

---

## 🎯 Next Actions

1. ✅ **Local test**: `streamlit run streamlit_app.py`
2. ✅ **Validate**: `python test_app.py`
3. ✅ **Push to GitHub**: Make repo public
4. ✅ **Deploy to Cloud**: share.streamlit.io → "New app"
5. ✅ **Share**: Post the link online

---

**Questions?** See `README.md` (full docs) or `DEPLOYMENT_GUIDE.md` (step-by-step)
