import pandas as pd
import joblib
import os

from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score


MODEL_PATH = "spam_model.joblib"


def train_model():
    train_df = pd.read_csv("data/train.csv")
    test_df = pd.read_csv("data/test.csv")

    X_train = train_df["text"].astype(str).values
    y_train = train_df["label"].astype(int).values

    X_test = test_df["text"].astype(str).values
    y_test = test_df["label"].astype(int).values

    model = Pipeline([
        ("vectorizer", CountVectorizer(
            analyzer="char",
            ngram_range=(3, 5),
            max_features=20000,
            lowercase=True
        )),
        ("classifier", LogisticRegression(
            max_iter=2000,
            class_weight="balanced"
        ))
    ])

    model.fit(X_train, y_train)

    pred = model.predict(X_test)

    print("Accuracy:", accuracy_score(y_test, pred))
    print()
    print(classification_report(y_test, pred, digits=4))
    print()
    print(confusion_matrix(y_test, pred))

    joblib.dump(model, MODEL_PATH)
    print(f"\nSaved model to {MODEL_PATH}")

    return model


def load_model():
    return joblib.load(MODEL_PATH)


def predict_probability(model, text: str):
    """
    Returns probability of spam label 1.
    """
    prob = model.predict_proba([text])[0][1]
    return prob


def interactive_predict():
    model = load_model()

    print("Interactive spam detector")
    print("Type a message and press Enter.")
    print("Type /quit to exit.")
    print()

    while True:
        text = input("> ")

        if text.strip().lower() in ["/quit", "quit", "exit"]:
            break

        prob = predict_probability(model, text)
        label = int(prob >= 0.5)

        print(f"spam_probability={prob:.4f} label={label}")

        if prob >= 0.9:
            print("very likely spam")
        elif prob >= 0.7:
            print("likely spam")
        elif prob >= 0.5:
            print("maybe spam")
        else:
            print("probably normal")

        print()


if __name__ == "__main__":
    # Train once, then comment this out if model already exists.
    if not os.path.exists(MODEL_PATH):
      train_model()

    # Then test interactively.
    interactive_predict()
