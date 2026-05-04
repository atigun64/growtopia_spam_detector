Growtopia spam/benign example generator

This repository contains tools to synthesize Growtopia-style chat messages for training a spam detector. It includes:

- generators/grammars that produce positive (spam) and negative (benign) messages
- normalization utilities in `normalization.py`
- data generation helpers in `generate_data/`
- a dataset generator script: `generate_data/make_dataset.py` that outputs CSV splits

Quick start

1. Create and activate a Python virtualenv:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Generate a dataset (example):

```bash
python3 generate_data/make_dataset.py --n 2000 --outdir generated_data --seed 2026
```

4. Normalize and inspect examples:

```bash
python3 main.py
```

