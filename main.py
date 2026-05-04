from normalization import text_normalize
import pandas as pd
import os

CSV_PATH = os.path.join('generated_data', 'train.csv')


def load_examples(path, n=100):
    df = pd.read_csv(path)
    return df['text'].astype(str).tolist()[:n]

if __name__ == '__main__':
    if not os.path.exists(CSV_PATH):
        print(f"CSV not found: {CSV_PATH}. Please run generate_data/make_dataset.py first.")
        raise SystemExit(1)

    # examples = load_examples(CSV_PATH, n=100)

    examples = [
        "CSN---=---GO----TO-----REMECAN1421"
    ]

    for ex in examples:
        print('original: ', ex)
        print('normalized:', text_normalize(ex))
        print()