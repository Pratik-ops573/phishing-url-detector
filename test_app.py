"""
Test script for Phishing URL Detector

Validates:
1. Model and features can be loaded
2. Feature extraction returns expected structure
3. Feature vector can be built in correct order
4. Predictions work end-to-end
"""

import joblib
import sys


def test_model_loading():
    """Test that model and features can be loaded."""
    print("=" * 60)
    print("TEST 1: Loading Model & Features")
    print("=" * 60)
    
    try:
        model = joblib.load("Phishing_url_model.pkl")
        print(f"✓ Model loaded successfully")
        print(f"  - Type: {type(model).__name__}")
        print(f"  - Expected features: {model.n_features_in_}")
        
        features = joblib.load("phishing_url_features.pkl")
        print(f"✓ Features list loaded successfully")
        print(f"  - Total features: {len(features)}")
        print(f"  - First 5 features: {features[:5]}")
        print(f"  - Last 5 features: {features[-5:]}")
        
        # Verify consistency
        if model.n_features_in_ == len(features):
            print(f"✓ Model and feature list match: {len(features)} features")
        else:
            print(f"✗ MISMATCH: Model expects {model.n_features_in_}, "
                  f"but feature list has {len(features)}")
            return False
        
        return model, features
    
    except Exception as e:
        print(f"✗ Error loading artifacts: {e}")
        return False, False


def test_feature_extraction():
    """Test feature extraction on sample URLs."""
    print("\n" + "=" * 60)
    print("TEST 2: Feature Extraction (URL-level only, no network calls)")
    print("=" * 60)
    
    try:
        # Import the feature extraction module
        from feature_extraction import _extract_url_features, build_feature_vector
        
        test_urls = [
            "https://www.google.com",
            "https://www.amazon.com/login",
            "http://suspicious-bank-login.xyz/verify-account",
        ]
        
        for url in test_urls:
            print(f"\nURL: {url}")
            features = _extract_url_features(url)
            print(f"  - Extracted {len(features)} features")
            print(f"  - Sample features:")
            sample_keys = list(features.keys())[:5]
            for key in sample_keys:
                print(f"    • {key}: {features[key]}")
        
        print(f"\n✓ Feature extraction working correctly")
        return True
    
    except Exception as e:
        print(f"✗ Feature extraction error: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_prediction(model, features):
    """Test making a prediction."""
    print("\n" + "=" * 60)
    print("TEST 3: Prediction on Sample URLs")
    print("=" * 60)
    
    try:
        from feature_extraction import extract_all_features, build_feature_vector
        
        test_urls = [
            ("https://www.google.com", "LEGITIMATE"),
            ("https://www.paypal-verify-account.xyz/login", "PHISHING"),
        ]
        
        for url, expected in test_urls:
            print(f"\nURL: {url}")
            print(f"Expected: {expected}")
            
            # Extract features (will use fallback values for HTML/WHOIS/DNS)
            features_dict, fetch_succeeded = extract_all_features(url)
            print(f"  - Features extracted: {len(features_dict)}")
            print(f"  - Page fetch succeeded: {fetch_succeeded}")
            
            # Build feature vector
            try:
                feature_vector = build_feature_vector(features_dict, features)
                print(f"  - Feature vector size: {len(feature_vector)}")
                
                # Predict
                prediction = model.predict([feature_vector])[0]
                probability = model.predict_proba([feature_vector])[0]
                
                verdict = "PHISHING" if prediction == 1 else "LEGITIMATE"
                confidence = max(probability) * 100
                
                print(f"  - Prediction: {verdict} ({confidence:.1f}% confidence)")
                print(f"  - Probability: Legitimate={probability[0]:.4f}, Phishing={probability[1]:.4f}")
                
            except ValueError as ve:
                print(f"  ✗ Feature vector error: {ve}")
                return False
        
        print(f"\n✓ Predictions working correctly")
        return True
    
    except Exception as e:
        print(f"✗ Prediction error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n")
    print("🛡️  PHISHING URL DETECTOR - TEST SUITE")
    print("=" * 60)
    
    # Test 1: Model loading
    result = test_model_loading()
    if not result or not result[0]:
        print("\n✗ Tests FAILED at model loading")
        return False
    
    model, features = result
    
    # Test 2: Feature extraction
    if not test_feature_extraction():
        print("\n✗ Tests FAILED at feature extraction")
        return False
    
    # Test 3: Predictions
    if not test_prediction(model, features):
        print("\n✗ Tests FAILED at prediction")
        return False
    
    print("\n" + "=" * 60)
    print("✅ ALL TESTS PASSED!")
    print("=" * 60)
    print("\nYou can now run the Streamlit app with:")
    print("  streamlit run streamlit_app.py")
    print("=" * 60 + "\n")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
