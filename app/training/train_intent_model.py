import os
import json
import argparse
import joblib
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.metrics import classification_report

def load_json_dataset(path):
    import json
    rows = []

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    for block in raw["intents"]:
        intent = block["intent"]
        for text in block["text"]:
            rows.append({
                "text": text,
                "intent": intent
            })

    return pd.DataFrame(rows)


def load_csv_dataset(path):
    return pd.read_csv(path)

def main(args):
    # Load dataset
    if args.format.lower() == "csv":
        df = load_csv_dataset(args.input)
    elif args.format.lower() == "json":
        df = load_json_dataset(args.input)
    else:
        raise ValueError("Unsupported dataset format")

    # Check required columns
    if "text" not in df.columns or "intent" not in df.columns:
        raise ValueError("Dataset must have 'text' and 'intent' columns")

    print(f"Loaded {len(df)} rows from {args.input}")

    # Train / validation split
    train_df, valid_df = train_test_split(df, test_size=0.20, random_state=42, stratify=df["intent"])

    X_train = train_df["text"].astype(str)
    y_train = train_df["intent"].astype(str)
    X_valid = valid_df["text"].astype(str)
    y_valid = valid_df["intent"].astype(str)

    # Build classifier
    print("Training intent classifier...")

    model = Pipeline([
        ("vectorizer", TfidfVectorizer(
            lowercase=True,
            ngram_range=(1, 2),
            max_df=0.95,
            min_df=2
        )),
        ("classifier", LogisticRegression(
            solver="lbfgs", max_iter=1000, n_jobs=-1
        ))
    ])

    model.fit(X_train, y_train)

    # Save model
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    joblib.dump(model, args.output)
    print(f"Saved intent model to {args.output}")

    # Validate
    if len(valid_df) > 0:
        print("\nValidation report:")
        y_pred = model.predict(X_valid)
        print(classification_report(y_valid, y_pred))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train intent classifier")
    parser.add_argument("--input", required=True, help="Path to dataset (CSV or JSON)")
    parser.add_argument("--format", required=True, choices=["csv", "json"], help="Dataset format")
    parser.add_argument("--output", required=True, help="Where to save the model (e.g. intent_model.pkl)")
    args = parser.parse_args()
    main(args)
