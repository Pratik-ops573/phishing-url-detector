# Phishing URL Detector

A simple machine learning project to detect whether a URL is phishing or legitimate.

## Project Files

- `index.html` - Simple web interface to check URLs
- `PhishingML.ipynb` - Jupyter notebook with model training
- `Phishing_url_model.pkl` - Trained ML model
- `phishing_url_features.pkl` - Feature extraction helper
- `dataset_phishing.csv` - Dataset used for training

## How to Use

1. Open `index.html` in your browser.
2. Enter a URL in the input field.
3. Click "Check URL" to see the prediction.

## Requirements

- Python 3.x
- pandas, numpy, scikit-learn, jupyter (for running the notebook)
- Any modern web browser (for the UI)

## Note

The prediction logic in `index.html` uses a placeholder. Replace it with a call to the actual model for real predictions.
