from normalization import text_normalize
import joblib
import os

CSV_PATH = os.path.join('generated_data', 'train.csv')
MODEL_PATH = 'spam_model.joblib'

def load_examples(path, n=100):
    import pandas as pd
    df = pd.read_csv(path)
    return df['text'].astype(str).tolist()[:n]

def predict_spam_probability(text):
    """Predict spam probability using the trained model."""
    if not os.path.exists(MODEL_PATH):
        return None  # Model not available, return None
    
    try:
        model = joblib.load(MODEL_PATH)
        prob = model.predict_proba([text])[0][1]
        return float(prob)
    except Exception as e:
        print(f"Error predicting: {e}")
        return None

def format_verdict(prob):
    """Format probability as a verdict."""
    if prob >= 0.9:
        return f"{prob:.4f} 🚨 SPAM (very likely)"
    elif prob >= 0.7:
        return f"{prob:.4f} 🚨 SPAM (likely)"
    elif prob >= 0.5:
        return f"{prob:.4f} ⚠️  MAYBE SPAM"
    elif prob >= 0.3:
        return f"{prob:.4f} ✓ PROBABLY OK"
    else:
        return f"{prob:.4f} ✓ OK (unlikely spam)"

if __name__ == '__main__':
    print("=" * 90)
    print("GROWTOPIA SPAM DETECTOR - NORMALIZATION & PREDICTION DEMO")
    print("=" * 90)
    print()
    
    # Demo examples: mix of spam and benign
    demo_examples = [
        # SPAM EXAMPLES - Casino advertisements
        ("CSN=WORLD52", True),
        ("C$N=WORLD100", True),
        ("C-A-S-I-N-O/WORLD52", True),
        ("REME//TEROYAM213", True),
        ("BJ=WORLD99", True),
        ("/me CSN=CASINO123", True),
        
        # BENIGN EXAMPLES - Legitimate chat
        ("come join my farm", False),
        ("buying seeds 5wl", False),
        ("owner is player123", False),
        ("can someone help with mining", False),
        ("where is the white door", False),
        ("min price 10wl thanks", False),
        
        # EDGE CASES - Benign use of casino-related words
        ("stop spamming csn ads!", False),
        ("why do people say casino?", False),
        ("gas mask for sale 3wl", False),
        ("min price check please", False),
    ]
    
    # Check if model is available
    model_available = os.path.exists(MODEL_PATH)
    
    if model_available:
        print("✓ Model loaded successfully")
    else:
        print("⚠ Model not found. Showing normalization only.")
        print(f"  To use predictions, train and save model to: {MODEL_PATH}")
    
    print()
    print("-" * 90)
    print("EXAMPLE MESSAGES & NORMALIZATION")
    print("-" * 90)
    print()
    
    # Group by spam/benign for clearer display
    spam_examples = [ex for ex, is_spam in demo_examples if is_spam]
    benign_examples = [ex for ex, is_spam in demo_examples if not is_spam]
    
    # Show spam examples
    print("SPAM EXAMPLES (Casino Advertisements):")
    print()
    for example in spam_examples:
        normalized = text_normalize(example)
        print(f"  Original:   {example}")
        print(f"  Normalized: {normalized}")
        
        if model_available:
            prob = predict_spam_probability(example)
            verdict = format_verdict(prob)
            print(f"  Prediction: {verdict}")
        print()
    
    print("-" * 90)
    print()
    print("BENIGN EXAMPLES (Legitimate Chat):")
    print()
    for example in benign_examples:
        normalized = text_normalize(example)
        print(f"  Original:   {example}")
        print(f"  Normalized: {normalized}")
        
        if model_available:
            prob = predict_spam_probability(example)
            verdict = format_verdict(prob)
            print(f"  Prediction: {verdict}")
        print()
    
    print("-" * 90)
    print()
    
    # Option to test custom input
    print("CUSTOM TEST:")
    print("Edit 'examples' list in main.py to test different messages.")
    print()
    
    if not model_available:
        print("NOTE: Model predictions require a trained spam_model.joblib file.")
        print("Train and save the model using sklearn or another ML framework.")
        print()