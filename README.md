# Growtopia Spam Detector

A machine learning-based spam detector for Growtopia (a multiplayer sandbox game) that distinguishes between **casino/gambling advertisements** and **legitimate player chat**.

## Overview

This project detects casino-related spam messages in Growtopia chat, which often disguise gambling advertisements using:
- **Direct tokens**: `CSN`, `CASINO`, `BJ`, `REME`, `BEJE`
- **Obfuscated forms**: `C$N`, `C4S1N0`, `C-S-N`, `CSN//WORLD52`
- **Separators**: `=`, `/`, `:`, `-` used to structure ads like `CSN=WORLD52`

Legitimate messages (world invites, trades, gameplay chat) are unaffected.

## Project Structure

```
growtopia_spam_detector/
├── app.py                          # Gradio web interface for the detector
├── main.py                         # Demo script with normalization examples
├── normalization.py                # Text normalization utilities
├── spam_model.joblib               # Trained ML model
├── requirements.txt                # Dependencies
├── data/                           # Datasets
│   ├── train.csv
│   ├── val.csv
│   └── test.csv
└── generate_data/                  # Synthetic data generation
    ├── main.py                     # Grammar generation demo
    ├── make_dataset.py             # Generate train/val/test splits
    ├── generator.py                # Grammar engine
    ├── helper.py                   # Text manipulation utilities
    ├── bid_name_generator.py       # Casino token generation (spam)
    ├── world_name_generator.py     # World name generation
    └── grammars/
        ├── positive.py             # Spam message patterns
        └── negative/               # Benign message patterns (modularized)
            ├── __init__.py
            ├── base.py             # Shared utilities & constants
            ├── world_invites.py    # "come join my world"
            ├── trade_messages.py   # "buying/selling items"
            ├── owner_info.py       # "owner is USERNAME"
            ├── help_social.py      # "how do I farm?"
            ├── hard_negatives.py   # Edge cases with benign use of casino terms
            ├── casino_discussion_negatives.py  # "stop spamming CSN"
            ├── aggressive_intent.py            # "go go go!!"
            ├── random_gibberish.py            # "asdfghjkl"
            └── gameplay_negative.py           # Normal gameplay chat
```

## Installation

1. Create and activate a Python virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### Option 1: Web Interface

Launch the Gradio demo (requires a trained model):

```bash
python3 app.py
```

Then open `http://localhost:7860` in your browser. Type a message to get a spam probability score.

**Example usage in app.py:**
```python
# app.py loads the trained model and provides predictions
model = joblib.load("spam_model.joblib")
prob = model.predict_proba([text])[0][1]  # Spam probability
label = 0 if prob < 0.5 else 1              # Classification
```

### Option 2: Python API

```python
import joblib

# Load the model
model = joblib.load("spam_model.joblib")

# Predict on a message
text = "CSN=WORLD52"
prob = model.predict_proba([text])[0][1]
print(f"Spam probability: {prob:.4f}")
print(f"Label: {'SPAM' if prob >= 0.5 else 'BENIGN'}")
```

## Demo: Spam Detection Examples

### Spam Messages (Caught)

These casino advertisement variants are correctly classified as spam:

```
Input                      Normalized              Probability
────────────────────────────────────────────────────────────────
CSN=WORLD52               csn world52             0.9997 🚨 SPAM
C$N=WORLD100              cn world100             0.9866 🚨 SPAM
C-A-S-I-N-O/WORLD52       c-a-s-i-n-o/world52    0.9910 🚨 SPAM
REME//TEROYAM213          reme//teroyam213        0.9966 🚨 SPAM
BJ=WORLD99                bj world99              0.9920 🚨 SPAM
/me CSN=CASINO123         csn casino123           1.0000 🚨 SPAM
```

**Key patterns detected:**
- Casino token (`CSN`, `CASINO`, `REME`, `BJ`, `BEJE`)
- Separator patterns (`=`, `//`, `-`, `:`)
- World identifier following the token
- Obfuscated forms (leet-speak: `C$N`, `C4S1N0`, etc.)

### Benign Messages (Pass Through)

Legitimate Growtopia chat is classified correctly as benign:

```
Input                              Normalized                Probability
────────────────────────────────────────────────────────────────────────
come join my farm                  come join my farm         0.0004 ✓ OK
buying seeds 5wl                   buying seeds 5wl          0.0002 ✓ OK
owner is player123                 owner is player123        0.0000 ✓ OK
can someone help with mining       can someone help mining   0.0000 ✓ OK
where is the white door            where is white door       0.0000 ✓ OK
min price 10wl thanks              min price 10wl thanks     0.0000 ✓ OK
```

**Why they pass:**
- No casino tokens (or benign use: "min" = minimum price)
- Normal Growtopia vocabulary (farm, world, wl/dl currency)
- Legitimate action verbs (join, buy, help)

### Edge Cases (Hard Negatives)

Some messages use casino-related tokens but are NOT advertisements:

```
Input                           Normalized              Probability
─────────────────────────────────────────────────────────────────
stop spamming csn ads!          stop spamming csn ads   0.0208 ✓ OK
why do people say casino?       why people say casino   0.0003 ✓ OK
gas mask for sale 3wl           gas mask for sale 3wl   0.0001 ✓ OK
min price check please          min price check         0.0000 ✓ OK
```

**Why they're correctly classified as benign:**
- Anti-spam sentiment ("stop spamming")
- Discussion about casino spam (not promoting it)
- Benign use of "GAS" (gas mask item) and "MIN" (minimum price)
- Context makes intent clear

## Data Generation

Generate synthetic training data:

```bash
python3 generate_data/make_dataset.py --n 5000 --outdir generated_data --seed 2026
```

This creates:
- `train.csv` (80%): Training data with `text` and `label` columns
- `val.csv` (10%): Validation data
- `test.csv` (10%): Test data

The generator uses two modular grammar systems:

- **Positive Grammar** (`generate_data/grammars/positive.py`): Generates casino spam variants
- **Negative Grammar** (`generate_data/grammars/negative/`): Generates diverse benign chat

## How It Works

1. **Feature Extraction** (via sklearn):
   - TF-IDF vectorization of normalized text
   - Captures token frequency patterns

2. **Classification** (trained model):
   - Binary classifier: Spam (1) vs. Benign (0)
   - Outputs probability [0, 1]
   - Threshold: 0.5 (≥0.5 = spam)

## Files Reference

| File | Purpose |
|------|---------|
| `app.py` | Gradio web interface for real-time detection |
| `main.py` | Demo script; edit to test normalization |
| `spam_model.joblib` | Trained ML model (binary classifier) |
| `generate_data/make_dataset.py` | Generate synthetic training/test data |
| `generate_data/grammars/positive.py` | Casino spam message patterns |
| `generate_data/grammars/negative/` | Benign chat patterns (modular structure) |
