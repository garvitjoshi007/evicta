import joblib
MODEL = joblib.load("models/intent_model.pkl")

def classify_intent(prompt: str) -> str:
    return MODEL.predict([prompt])[0]