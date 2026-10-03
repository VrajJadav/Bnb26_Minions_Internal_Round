import random
import re

import pandas as pd
from sklearn.ensemble import RandomForestClassifier

LABELS = [
    "correct",
    "distribute_first_only",
    "ignore_minus_sign",
    "square_each_term",
    "multiply_by_two",
]

DISPLAY_LABELS = {
    "distribute_first_only": "Only distributing to the first term",
    "ignore_minus_sign": "Losing the minus sign",
    "square_each_term": "Missing the middle term when squaring",
    "multiply_by_two": "Treating a square like multiplication by 2",
}


def normalize_answer(answer):
    if answer is None:
        return ""

    return (
        str(answer)
        .strip()
        .lower()
        .replace(" ", "")
        .replace("X", "x")
        .replace("²", "^2")
        .replace("*", "")
    )


def parse_expression(question):
    q = normalize_answer(question)

    match = re.fullmatch(r"(\d+)\(x\+(\d+)\)", q)
    if match:
        return {
            "type": "plus",
            "a": int(match.group(1)),
            "b": int(match.group(2)),
        }

    match = re.fullmatch(r"(\d+)\(x-(\d+)\)", q)
    if match:
        return {
            "type": "minus",
            "a": int(match.group(1)),
            "b": int(match.group(2)),
        }

    match = re.fullmatch(r"\(x\+(\d+)\)\^2", q)
    if match:
        return {
            "type": "square",
            "a": 1,
            "b": int(match.group(1)),
        }

    raise ValueError(
        "Unsupported expression. Use formats such as "
        "4(x+3), 5(x-2), or (x+4)^2."
    )


def get_correct_answer(question):
    data = parse_expression(question)
    a, b = data["a"], data["b"]

    if data["type"] == "square":
        return f"x^2+{2*b}x+{b*b}"

    if data["type"] == "minus":
        return f"{a}x-{a*b}"

    return f"{a}x+{a*b}"


def evaluate_expression(expression, x):
    try:
        e = normalize_answer(expression).replace("^", "**")

        e = re.sub(r"(\d)(x|\()", r"\1*\2", e)
        e = re.sub(r"(x|\))(\d|x|\()", r"\1*\2", e)

        if not re.fullmatch(r"[0-9x+\-*/().]+", e):
            return None

        if len(e) > 60:
            return None

        if "**" in e:
            if e.count("**") > 1 or "**2" not in e:
                return None

        return eval(
            e,
            {"__builtins__": {}},
            {"x": x},
        )

    except Exception:
        return None


def are_equivalent(expression_1, expression_2):
    for x in [-5, -2, 0, 1, 2, 5, 9]:
        value_1 = evaluate_expression(expression_1, x)
        value_2 = evaluate_expression(expression_2, x)

        if value_1 is None or value_2 is None:
            return False

        if value_1 != value_2:
            return False

    return True


def check_answer(question, answer):
    correct = get_correct_answer(question)
    return are_equivalent(answer, correct), correct


def deterministic_diagnosis(question, answer):
    try:
        data = parse_expression(question)
        a, b = data["a"], data["b"]
        normalized = normalize_answer(answer)

        if data["type"] == "plus":
            if normalized == f"{a}x+{b}":
                return "distribute_first_only", 100

        if data["type"] == "minus":
            if normalized == f"{a}x+{a*b}":
                return "ignore_minus_sign", 100

        if data["type"] == "square":
            if normalized == f"x^2+{b*b}":
                return "square_each_term", 100

            if normalized == f"2x+{2*b}":
                return "multiply_by_two", 100

    except Exception:
        pass

    return None, 0


def make_training_row(label):
    a = random.randint(2, 9)
    b = random.randint(2, 9)

    if label == "correct":
        kind = random.choice(["plus", "minus", "square"])

        if kind == "plus":
            question = f"{a}(x+{b})"
            answer = f"{a}x+{a*b}"
        elif kind == "minus":
            question = f"{a}(x-{b})"
            answer = f"{a}x-{a*b}"
        else:
            question = f"(x+{b})^2"
            answer = f"x^2+{2*b}x+{b*b}"

    elif label == "distribute_first_only":
        question = f"{a}(x+{b})"
        answer = f"{a}x+{b}"

    elif label == "ignore_minus_sign":
        question = f"{a}(x-{b})"
        answer = f"{a}x+{a*b}"

    elif label == "square_each_term":
        question = f"(x+{b})^2"
        answer = f"x^2+{b*b}"

    else:
        question = f"(x+{b})^2"
        answer = f"2x+{2*b}"

    return {
        "question": question,
        "answer": answer,
        "a": a,
        "b": b,
        "label": label,
    }


def build_data(n_per_label=160):
    rows = [
        make_training_row(label)
        for label in LABELS
        for _ in range(n_per_label)
    ]
    return pd.DataFrame(rows)


def features(question, answer, a, b):
    q = normalize_answer(question)
    ans = normalize_answer(answer)

    qtype = 2 if "^2" in q else 1 if "-" in q else 0

    match = re.fullmatch(r"(\d*)x(\^2)?([+-]\d+)", ans)

    if not match:
        return [
            qtype, a, b, 0, 0, 0, 1, 0,
            0, 0, 0, 0, 0, 0
        ]

    coefficient = int(match.group(1) or 1)
    constant = int(match.group(3))

    return [
        qtype,
        a,
        b,
        int(match.group(2) is not None),
        coefficient,
        constant,
        int(constant == b),
        int(constant == a*b),
        int(constant == b*b),
        int(constant == 2*b),
        int(coefficient == a),
        int(coefficient == 2),
        int(constant < 0),
        int("x^2" in ans),
    ]


def train_model():
    df = build_data()

    X = [
        features(row.question, row.answer, row.a, row.b)
        for row in df.itertuples()
    ]

    model = RandomForestClassifier(
        n_estimators=160,
        random_state=42,
        max_depth=12,
        class_weight="balanced",
        n_jobs=-1,
    )

    model.fit(X, df.label)
    return model


_MODEL = None


def get_model():
    global _MODEL

    if _MODEL is None:
        _MODEL = train_model()

    return _MODEL


def diagnose_mistake(question, answer):
    label, confidence = deterministic_diagnosis(question, answer)

    if label:
        return label, confidence

    model = get_model()
    parsed = parse_expression(question)

    row = features(
        question,
        answer,
        parsed["a"],
        parsed["b"],
    )

    probabilities = model.predict_proba([row])[0]

    results = sorted(
        zip(model.classes_, probabilities),
        key=lambda item: item[1],
        reverse=True,
    )

    label = results[0][0]
    confidence = round(results[0][1] * 100)

    return label, confidence


def get_lesson(label, question=None):
    a, b = 2, 3

    if question:
        try:
            parsed = parse_expression(question)
            a, b = parsed["a"], parsed["b"]
        except Exception:
            pass

    explanations = {
        "distribute_first_only": (
            f"You multiplied only the first term by {a}. "
            f"The {b} must also be multiplied: "
            f"{a} × {b} = {a*b}."
        ),
        "ignore_minus_sign": (
            f"The minus sign changes the final term. "
            f"{a}(x-{b}) becomes {a}x-{a*b}, not {a}x+{a*b}."
        ),
        "square_each_term": (
            f"Squaring the bracket creates a middle term. "
            f"(x+{b})² = x² + {2*b}x + {b*b}. "
            f"The middle {2*b}x cannot be skipped."
        ),
        "multiply_by_two": (
            f"Squaring is different from doubling. "
            f"(x+{b})² means (x+{b})(x+{b}), not 2(x+{b})."
        ),
    }

    return explanations.get(
        label,
        "The model detected an algebra misconception.",
    )


def generate_question(misconception=None):
    a = random.randint(2, 9)
    b = random.randint(2, 9)

    if misconception in [
        "distribute_first_only",
        "Only distributing to the first term",
    ]:
        return f"{a}(x+{b})"

    if misconception in [
        "ignore_minus_sign",
        "Losing the minus sign",
    ]:
        return f"{a}(x-{b})"

    if misconception in [
        "square_each_term",
        "Missing the middle term when squaring",
        "multiply_by_two",
        "Treating a square like multiplication by 2",
    ]:
        return f"(x+{b})^2"

    return random.choice([
        f"{a}(x+{b})",
        f"{a}(x-{b})",
        f"(x+{b})^2",
    ])


def get_retest_questions(label):
    questions = []

    while len(questions) < 3:
        question = generate_question(label)
        if question not in questions:
            questions.append(question)

    return questions


def validate_question(question):
    if not question.strip():
        return False, "Please enter a question."

    try:
        parse_expression(question)
        return True, "Valid expression."
    except Exception:
        return (
            False,
            "Use 4(x+3), 5(x-2), or (x+4)^2.",
        )
