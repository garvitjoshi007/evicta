import joblib
import spacy

MODEL = joblib.load("app/training/models/intent_model.pkl")

nlp = spacy.load("en_core_web_sm")

def extract_subject(prompt):
    doc = nlp(prompt)
    for chunk in doc.noun_chunks:
        return chunk.text.lower()
    return None


def classify_intent(prompt: str) -> str:
    return MODEL.predict([prompt])[0]


def extract_intent(prompt: str) -> str | None:
    prompt = prompt.lower().strip()
    try:
        intent = classify_intent(prompt)
        subject = extract_subject(prompt)
        return f"{intent}:{subject}"
    except Exception as err:
        return None


# print(classify_intent("explain neural networks"))
# print(extract_subject("explain neural networks"))