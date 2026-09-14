"""
Phishing URL Detector - Streamlit Web App

A machine learning-powered web app that detects phishing URLs using a trained
Random Forest classifier with 80 URL/content/domain features.

Model accuracy: ~96.3% on test set
"""

import streamlit as st
import joblib
import pandas as pd
from feature_extraction import extract_all_features, build_feature_vector
import traceback


# ============================================================================
# PAGE CONFIG & CACHING
# ============================================================================

st.set_page_config(
    page_title="Phishing URL Detector",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)


@st.cache_resource
def load_model_and_features():
    """Load the trained model and feature names (cached for performance)."""
    try:
        model = joblib.load("phishing_url_model.pkl")
        features = joblib.load("phishing_url_features.pkl")
        return model, features
    except FileNotFoundError as e:
        st.error(f"❌ Model files not found: {e}")
        st.stop()


# ============================================================================
# MAIN APP
# ============================================================================

def main():
    st.title("🛡️ Phishing URL Detector")
    st.markdown(
        "Check whether a URL is **legitimate** or **phishing** using machine learning."
    )

    # Sidebar with disclaimer and info
    with st.sidebar:
        st.header("ℹ️ About")
        st.markdown(
            """
            This tool uses a **Random Forest classifier** trained on ~50k labeled URLs
            to predict phishing likelihood.
            
            **Model Performance:**
            - Accuracy: ~96.3%
            - Precision: ~96%
            - Recall: ~97%
            
            **Note:** This is a heuristic, not a guarantee. Always exercise judgment
            with unfamiliar links, and never enter credentials into suspicious pages.
            """
        )
        
        st.markdown("---")
        st.markdown(
            "📊 **Features analyzed:**\n"
            "- URL structure & length\n"
            "- Hostname characteristics\n"
            "- Page content & HTML elements\n"
            "- Domain registration (WHOIS)\n"
            "- DNS resolution\n"
            "- Phishing keyword hints"
        )
        
        st.markdown("---")
        st.caption("⚙️ Deployment: Streamlit Community Cloud")

    # Load model
    model, feature_names = load_model_and_features()

    # URL Input
    st.subheader("Enter a URL to Check")
    url_input = st.text_input(
        "URL:",
        placeholder="e.g., https://www.google.com or amazon.com",
        label_visibility="collapsed"
    )

    if st.button("🔍 Check URL", type="primary", use_container_width=True):
        if not url_input or not url_input.strip():
            st.error("⚠️ Please enter a URL.")
        else:
            # Normalize URL
            url = url_input.strip()
            if not url.startswith(("http://", "https://")):
                url = "https://" + url

            # Extract features with spinner
            with st.spinner("🔄 Analyzing URL... (this may take a few seconds)"):
                try:
                    features_dict, fetch_succeeded = extract_all_features(url)
                    feature_vector = build_feature_vector(features_dict, feature_names)

                    # Make prediction
                    prediction = model.predict([feature_vector])[0]
                    probability = model.predict_proba([feature_vector])[0]

                    # Display verdict
                    st.markdown("---")
                    col1, col2 = st.columns([2, 1])

                    with col1:
                        if prediction == 1:  # Phishing
                            st.markdown(
                                '<div style="padding: 20px; background-color: #ffebee; border-radius: 8px; border-left: 5px solid #d32f2f;">'
                                '<h2 style="color: #d32f2f; margin: 0;">⚠️ Likely Phishing</h2>'
                                '<p style="color: #c62828; margin-top: 10px; font-size: 16px;">This URL exhibits characteristics typical of phishing attempts.</p>'
                                '</div>',
                                unsafe_allow_html=True
                            )
                        else:  # Legitimate
                            st.markdown(
                                '<div style="padding: 20px; background-color: #e8f5e9; border-radius: 8px; border-left: 5px solid #388e3c;">'
                                '<h2 style="color: #388e3c; margin: 0;">✅ Likely Legitimate</h2>'
                                '<p style="color: #2e7d32; margin-top: 10px; font-size: 16px;">This URL appears to be safe based on structural analysis.</p>'
                                '</div>',
                                unsafe_allow_html=True
                            )

                    with col2:
                        st.metric(
                            "Confidence",
                            f"{max(probability) * 100:.1f}%",
                            delta=None
                        )

                    # Fetch warning
                    if not fetch_succeeded:
                        st.info(
                            "ℹ️ **Page content could not be fetched.** "
                            "The prediction is based on URL structure only, which may reduce accuracy."
                        )

                    # Expandable features section
                    with st.expander("📊 View Extracted Features (80 total)"):
                        # Create a DataFrame for better visualization
                        features_df = pd.DataFrame({
                            "Feature": list(features_dict.keys()),
                            "Value": list(features_dict.values())
                        })
                        
                        # Round numeric values for readability
                        features_df["Value"] = features_df["Value"].apply(
                            lambda x: round(x, 4) if isinstance(x, float) else x
                        )
                        
                        # Display in columns for easier scanning
                        st.dataframe(features_df, use_container_width=True, hide_index=True)
                        
                        # Summary statistics
                        col1, col2, col3 = st.columns(3)
                        col1.metric("Total Features", len(features_dict))
                        col2.metric("Zero-valued Features", sum(1 for v in features_dict.values() if v == 0))
                        col3.metric("Fetch Succeeded", "✅ Yes" if fetch_succeeded else "❌ No")

                except ValueError as e:
                    st.error(f"❌ Feature extraction error: {e}")
                except Exception as e:
                    st.error(f"❌ An error occurred: {str(e)}")
                    with st.expander("🐛 Error Details"):
                        st.code(traceback.format_exc())

    # Footer
    st.markdown("---")
    st.caption(
        "🔒 **Privacy:** This app only sends your URL to public APIs for page/WHOIS/DNS lookups. "
        "No data is logged or stored."
    )


if __name__ == "__main__":
    main()
