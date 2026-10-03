import random, re
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

def make_row(label):
    a, b = random.randint(2, 9), random.randint(2, 9)
    if label == "correct":
        kind = random.choice(["plus", "minus", "square"])
        if kind == "plus":   q, ans = f"{a}(x+{b})", f"{a}x+{a*b}"
        if kind == "minus":  q, ans = f"{a}(x-{b})", f"{a}x-{a*b}"
        if kind == "square": q, ans = f"(x+{b})^2", f"x^2+{2*b}x+{b*b}"
    elif label == "distribute_first_only":   # 2(x+3) -> 2x+3
        q, ans = f"{a}(x+{b})", f"{a}x+{b}"
    elif label == "ignore_minus_sign":       # 2(x-3) -> 2x+6
        q, ans = f"{a}(x-{b})", f"{a}x+{a*b}"
    elif label == "square_each_term":        # (x+3)^2 -> x^2+9
        q, ans = f"(x+{b})^2", f"x^2+{b*b}"
    elif label == "multiply_by_two":         # (x+3)^2 -> 2x+6
        q, ans = f"(x+{b})^2", f"2x+{2*b}"
    return {"question": q, "answer": ans, "a": a, "b": b, "label": label}

def features(q, ans, a, b):
    """Turn a question + answer into numbers the model can learn from."""
    ans = ans.replace(" ", "")
    qtype = 2 if "^2" in q else (1 if "-" in q else 0)
    m = re.match(r"(\d*)x(\^2)?([+-]\d+)$", ans)
    if not m:  # answer has a different shape (e.g. a correct square expansion)
        return [qtype, a, b, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0]
    coef = int(m.group(1) or 1)
    const = int(m.group(3))
    return [qtype, a, b, int(bool(m.group(2))), coef, const, 0,
            int(const == b), int(const == a*b), int(const == b*b),
            int(const == 2*b), int(coef == a), int(coef == 2), int(const < 0)]

LABELS = ["correct", "distribute_first_only", "ignore_minus_sign",
          "square_each_term", "multiply_by_two"]

def build_data(n_per_label=300):
    rows = [make_row(l) for l in LABELS for _ in range(n_per_label)]
    return pd.DataFrame(rows)

def train(df):
    X = [features(r.question, r.answer, r.a, r.b) for r in df.itertuples()]
    return RandomForestClassifier(n_estimators=100, random_state=0).fit(X, df.label)

def diagnose(model, q, ans, a, b):
    return model.predict([features(q, ans, a, b)])[0]

def diagnose_detailed(model, q, ans, a, b):
    """Returns all labels ranked by probability, e.g. [('square_each_term', 0.93), ...]"""
    probs = model.predict_proba([features(q, ans.replace(" ", ""), a, b)])[0]
    return sorted(zip(model.classes_, probs), key=lambda x: -x[1])

def explain(label, a, b):
    """A plain-language 'why we think this' line for each misconception."""
    return {
        "distribute_first_only": f"You multiplied only the first term by {a}. The {b} should also be multiplied: {a} x {b} = {a*b}.",
        "ignore_minus_sign": f"Your last term is +{a*b}, but the minus sign should make it -{a*b}.",
        "square_each_term": f"You squared {b} to get {b*b} but missed the middle term {2*b}x that comes from multiplying everything by everything.",
        "multiply_by_two": f"Your answer looks like 2(x+{b}), but squaring means (x+{b}) times (x+{b}), not doubling.",
    }.get(label, "")

if __name__ == "__main__":
    df = build_data()
    train_df, test_df = train_test_split(df, test_size=0.2, random_state=0)
    model = train(train_df)
    Xt = [features(r.question, r.answer, r.a, r.b) for r in test_df.itertuples()]
    preds = model.predict(Xt)
    print(classification_report(test_df.label, preds))
    print(confusion_matrix(test_df.label, preds, labels=LABELS))
