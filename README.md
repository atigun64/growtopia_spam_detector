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

Pushing this project to GitHub

See the instructions in the repository root for commands to create a GitHub repository and push your code. You can use either the GitHub CLI (`gh`) or standard `git` with a Personal Access Token (PAT).

Contact

If you want me to prepare extra repo files (LICENSE, GitHub Actions CI, CODEOWNERS) or to help craft a minimal `setup.py`/`pyproject.toml`, tell me which license and I can add them.
