"""
Phishing URL Detector - Streamlit Web App

A machine learning-powered web app that detects phishing URLs using a trained
Random Forest classifier.

Model accuracy: ~96.3% on test set
"""

import streamlit as st
import joblib
import pandas as pd
import os
from feature_extraction import extract_all_features, build_feature_vector
import traceback


# ============================================================================
# PAGE CONFIG & CACHING
# ============================================================================

st.set_page_config(
    page_title="Phishing URL Detector",
    page_icon="shield",
    layout="centered",
    initial_sidebar_state="collapsed"
)


@st.cache_resource
def load_model_and_features():
    """Load the trained model and feature names (cached for performance)."""
    try:
        # Check current directory
        if not os.path.exists("phishing_url_model.pkl"):
            st.error("ERROR: Model file not found in current directory")
            st.stop()
        
        model = joblib.load("phishing_url_model.pkl")
        features = joblib.load("phishing_url_features.pkl")
        return model, features
    except Exception as e:
        st.error(f"ERROR: Could not load model files: {str(e)}")
        st.stop()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    # Title - Simple and Clean
    st.title("Phishing URL Detector")
    
    st.markdown("Enter a URL to check if it is legitimate or phishing")
    st.markdown("---")

    # Load model
    model, feature_names = load_model_and_features()

    # URL Input - Simple
    url_input = st.text_input(
        "URL:",
        placeholder="Example: https://www.google.com or amazon.com",
        label_visibility="collapsed"
    )

    # Check Button
    if st.button("Check URL", type="primary", use_container_width=True):
        if not url_input or not url_input.strip():
            st.error("Please enter a URL")
        else:
            # Normalize URL
            url = url_input.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Extract features with spinner
            with st.spinner("Analyzing URL..."):
                try:
                    features_dict, fetch_succeeded = extract_all_features(url)
                    feature_vector = build_feature_vector(features_dict, feature_names)

                    # Make prediction
                    prediction = model.predict([feature_vector])[0]
                    probability = model.predict_proba([feature_vector])[0]

                    # Display verdict - Clean and Simple
                    st.markdown("---")
                    
                    if prediction == 1:  # Phishing
                        st.error("PHISHING DETECTED")
                        col1, col2 = st.columns(2)
                        col1.metric("Result", "Phishing")
                        col2.metric("Confidence", f"{probability[1] * 100:.1f}%")
                    else:  # Legitimate
                        st.success("LEGITIMATE")
                        col1, col2 = st.columns(2)
                        col1.metric("Result", "Legitimate")
                        col2.metric("Confidence", f"{probability[0] * 100:.1f}%")

                    # Fetch warning
                    if not fetch_succeeded:
                        st.warning("Note: Page content could not be fetched. Result based on URL structure only.")

                    # Expandable features section
                    with st.expander("View All Features"):
                        features_df = pd.DataFrame({
                            "Feature": list(features_dict.keys()),
                            "Value": list(features_dict.values())
                        })
                        
                        features_df["Value"] = features_df["Value"].apply(
                            lambda x: round(x, 4) if isinstance(x, float) else x
                        )
                        
                        st.dataframe(features_df, use_container_width=True, hide_index=True)

                except ValueError as e:
                    st.error(f"Feature extraction error: {e}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")

    # Info in sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
**Accuracy:** 96.3%
**Precision:** 96%
**Recall:** 97%

**Model:** Random Forest trained on 50,000 URLs

**Features Analyzed:**
- URL structure
- Hostname characteristics
- Page content
- Domain registration
- DNS records
- Phishing keywords

**Disclaimer:** This is a heuristic tool. Always verify suspicious links independently.
        """)


if __name__ == "__main__":
    main()
