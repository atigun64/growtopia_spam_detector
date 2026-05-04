"""Generate a dataset of positive/negative examples using the project's grammars.

Produces CSV files: train.csv, val.csv, test.csv with columns: text,label

Usage:
    python3 generate_data/make_dataset.py --n 10000 --outdir data

This script depends on scikit-learn. Install with:
    pip install -r ../requirements.txt
"""

import os
import argparse
import csv
import random

# local imports
import sys
sys.path.insert(0, os.path.abspath('.'))
from generator import GrammarGenerator
from grammars.positive import install_positive_spam_grammar
from grammars.negative import install_negative_spam_grammar

try:
    from sklearn.model_selection import train_test_split
except Exception as exc:
    raise RuntimeError("scikit-learn is required for dataset splitting. Install with 'pip install scikit-learn'.") from exc


def generate_samples(n_pos, n_neg, seed=42):
    rng = random.Random(seed)

    G_pos = GrammarGenerator(seed=seed)
    install_positive_spam_grammar(G_pos)

    G_neg = GrammarGenerator(seed=seed+1)
    install_negative_spam_grammar(G_neg)

    pos = [G_pos.generate('{SPAM_MESSAGE}')[0] for _ in range(n_pos)]
    neg = [G_neg.generate('{NONSPAM_MESSAGE}')[0] for _ in range(n_neg)]

    texts = pos + neg
    labels = [1] * len(pos) + [0] * len(neg)

    # shuffle
    combined = list(zip(texts, labels))
    rng.shuffle(combined)
    texts, labels = zip(*combined)
    return list(texts), list(labels)


def write_csv(rows, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', newline='', encoding='utf8') as fh:
        writer = csv.writer(fh)
        writer.writerow(['text', 'label'])
        for t, l in rows:
            writer.writerow([t, l])


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--n', type=int, default=30000, help='total examples (split equally pos/neg)')
    p.add_argument('--outdir', type=str, default='data', help='output directory')
    p.add_argument('--seed', type=int, default=42)
    p.add_argument('--test-size', type=float, default=0.1)
    p.add_argument('--val-size', type=float, default=0.1)
    args = p.parse_args()

    n_each = max(1, args.n // 2)
    texts, labels = generate_samples(n_each, n_each, seed=args.seed)

    X_train, X_temp, y_train, y_temp = train_test_split(texts, labels, test_size=args.test_size + args.val_size, random_state=args.seed, stratify=labels)
    val_fraction = args.val_size / (args.test_size + args.val_size) if (args.test_size + args.val_size) > 0 else 0
    X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=val_fraction, random_state=args.seed, stratify=y_temp)

    out = args.outdir
    write_csv(zip(X_train, y_train), os.path.join(out, 'train.csv'))
    write_csv(zip(X_val, y_val), os.path.join(out, 'val.csv'))
    write_csv(zip(X_test, y_test), os.path.join(out, 'test.csv'))

    print(f'Wrote: {os.path.join(out, "train.csv")}, {os.path.join(out, "val.csv")}, {os.path.join(out, "test.csv")}')


if __name__ == '__main__':
    main()
