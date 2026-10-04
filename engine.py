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


EXTRA_LABELS = {
    "correct": "Unclassified mistake",
    "distribute_second_only": "Only multiplying the number",
    "added_instead_of_multiplied": "Adding instead of multiplying",
    "wrong_sign": "Getting the sign wrong",
    "dropped_variable": "Losing the x",
    "wrong_constant": "Wrong number at the end",
    "wrong_coefficient": "Wrong number in front of x",
    "wrong_terms": "Errors in both terms",
    "extra_square_term": "Adding an x\u00b2 term that doesn't belong",
    "middle_term_not_doubled": "Forgetting to double the middle term",
    "last_term_not_squared": "Not squaring the last term",
    "lost_square_term": "Losing the x\u00b2 term",
    "not_equivalent": "Answer doesn't match the question",
    "unreadable_answer": "Answer not in a readable form",
}

ALL_LABELS = {**DISPLAY_LABELS, **EXTRA_LABELS}


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
    """Rule-based diagnosis. Returns (label, confidence)."""
    try:
        return explain_mistake(question, answer)["label"], 100
    except Exception:
        return "unreadable_answer", 100


# ------------------------------------------------------------
# Rule-based explanation of a wrong answer
# ------------------------------------------------------------

def parse_polynomial(answer):
    """'2x+6' -> (0, 2, 6); 'x^2+25' -> (1, 0, 25); '12' -> (0, 0, 12)."""
    s = normalize_answer(answer).replace("\u2212", "-")

    if not s or not re.fullmatch(r"[0-9x+\-^]+", s):
        return None

    terms = re.findall(r"[+-]?[^+-]+", s)
    if "".join(terms) != s:
        return None

    poly = {2: 0, 1: 0, 0: 0}

    for term in terms:
        power = 2
        m = re.fullmatch(r"([+-]?)(\d*)x\^2", term)
        if not m:
            power = 1
            m = re.fullmatch(r"([+-]?)(\d*)x", term)
        if not m:
            power = 0
            m = re.fullmatch(r"([+-]?)(\d+)", term)
        if not m:
            return None

        value = int(m.group(2) or 1)
        poly[power] += -value if m.group(1) == "-" else value

    return poly[2], poly[1], poly[0]


def correct_polynomial(data):
    a, b = data["a"], data["b"]

    if data["type"] == "square":
        return 1, 2 * b, b * b
    if data["type"] == "minus":
        return 0, a, -a * b
    return 0, a, a * b


def _substituted(data, x):
    a, b = data["a"], data["b"]

    if data["type"] == "square":
        return f"({x}+{b})^2", (x + b) ** 2
    if data["type"] == "minus":
        return f"{a}({x}-{b})", a * (x - b)
    return f"{a}({x}+{b})", a * (x + b)


def _num(value):
    if isinstance(value, float) and value.is_integer():
        return int(value)
    return value


def _quick_check(data, answer):
    for x in (2, 1, 3, -1, 0):
        got = evaluate_expression(answer, x)
        if got is None:
            return None

        shown, expected = _substituted(data, x)
        if got != expected:
            return (
                f"Put `x = {x}` into both. The question gives "
                f"`{shown} = {expected}`, but your answer `{answer}` gives "
                f"`{_num(got)}`. A correct expansion always gives the same "
                f"number as the question."
            )
    return None


def worked_steps(data):
    a, b = data["a"], data["b"]

    if data["type"] == "square":
        return [
            f"Squaring means multiplying the bracket by itself: `(x+{b})^2 = (x+{b})(x+{b})`.",
            f"Multiply every term in the first bracket by every term in the second: `x\u00b7x + x\u00b7{b} + {b}\u00b7x + {b}\u00b7{b}`.",
            f"Work each one out: `x^2 + {b}x + {b}x + {b*b}`.",
            f"Combine the two middle terms: `x^2+{2*b}x+{b*b}`.",
        ]

    if data["type"] == "minus":
        return [
            f"The number outside multiplies every term inside, and each term keeps its own sign: `{a}(x-{b}) = {a}\u00b7x - {a}\u00b7{b}`.",
            f"Multiply the first pair: `{a}\u00b7x = {a}x`.",
            f"Multiply the second pair: `{a}\u00b7{b} = {a*b}`, and the minus sign stays in front of it.",
            f"Put them together: `{a}x-{a*b}`.",
        ]

    return [
        f"The number outside multiplies every term inside the bracket: `{a}(x+{b}) = {a}\u00b7x + {a}\u00b7{b}`.",
        f"Multiply the first pair: `{a}\u00b7x = {a}x`.",
        f"Multiply the second pair: `{a}\u00b7{b} = {a*b}`.",
        f"Put them together: `{a}x+{a*b}`.",
    ]


def _classify(data, question, ans, poly):
    """Return (label, summary, tip) describing what went wrong."""
    a, b, kind = data["a"], data["b"], data["type"]
    e2, e1, e0 = correct_polynomial(data)
    q = question.strip()
    inner = f"(-{b})" if kind == "minus" else f"{b}"

    if poly is None:
        readable = all(
            evaluate_expression(ans, x) is not None for x in (0, 1, 2)
        )
        if readable:
            return (
                "not_equivalent",
                f"Your answer `{ans}` is a valid expression, but it isn't equal to `{q}`. "
                "An expanded answer has to give the same value as the question for every value of `x`, not just one.",
                "Test your answer: put the same number in for `x` in the question and in your answer. If the results differ, something went wrong.",
            )
        return (
            "unreadable_answer",
            f"We couldn't read `{ans}` as an expression. Write the expanded answer using `x`, numbers, `+` and `-`.",
            "Write answers like `2x+6` or `x^2+6x+9`, with no brackets left in them.",
        )

    p2, p1, p0 = poly

    if kind in ("plus", "minus"):
        if p2 != 0:
            return (
                "extra_square_term",
                f"Your answer `{ans}` contains `x^2`, but `{q}` has only one `x` inside the bracket. "
                "Multiplying by a plain number never creates `x^2`; that only happens when `x` is multiplied by another `x`.",
                f"Multiplying by {a} scales each term. Neither the `x` nor the {b} turns into a square.",
            )

        if p1 == 0:
            return (
                "dropped_variable",
                f"Your answer `{ans}` is just a number, but `{q}` still has an unknown `x` once the bracket is removed. "
                f"A single number can only be right for one particular value of `x`, while the expansion has to work for every `x`. "
                f"The {a} multiplies the `x` too, giving `{a}x`, and that term has to stay in the answer.",
                "After expanding, an answer to this kind of question has an `x` term and a number term. They are different kinds of term and can't be merged into one number.",
            )

        if p1 == a:
            if p0 == -b or (kind == "plus" and p0 == b):
                return (
                    "distribute_first_only",
                    f"You wrote `{ans}`. The {a} was multiplied by the `x`, giving `{a}x`, but the {b} inside the bracket was left untouched. "
                    f"A number in front of a bracket multiplies every term inside it, so the {b} must be multiplied by {a} as well: `{a}\u00b7{b} = {a*b}`.",
                    "Draw one arrow from the outside number to each term inside the bracket. Two terms, two arrows, two multiplications.",
                )
            if kind == "minus" and p0 == a * b:
                return (
                    "ignore_minus_sign",
                    f"You wrote `{ans}`. Your multiplication is right, `{a}\u00b7{b} = {a*b}`, but the minus sign got lost on the way. "
                    f"The bracket contains `x-{b}`, so the number being multiplied is really negative: `{a}\u00b7(-{b}) = -{a*b}`.",
                    f"Treat `x-{b}` as `x+(-{b})` and multiply the sign along with the number. A positive times a negative is negative.",
                )
            if kind == "plus" and p0 == a + b:
                return (
                    "added_instead_of_multiplied",
                    f"You wrote `{ans}`. The `{p0}` looks like `{a}+{b}`. The number outside the bracket has to multiply the {b}, not be added to it: `{a}\u00b7{b} = {a*b}`.",
                    "A number written right next to a bracket means multiplication. There is no plus sign hiding between them.",
                )
            if kind == "plus" and p0 == -e0:
                return (
                    "wrong_sign",
                    f"You wrote `{ans}`, so the last term has the wrong sign. Inside the bracket the {b} is added, and `{a}\u00b7{b} = {a*b}` is positive, so the term is `+{a*b}`, not `-{a*b}`.",
                    "Look at the sign in front of each term inside the bracket and carry it into your answer.",
                )
            return (
                "wrong_constant",
                f"You wrote `{ans}`. The `x` term `{a}x` is right, but the number at the end is `{p0}` instead of `{e0}`. "
                f"To get it, multiply the outside number by the number inside the bracket: `{a}\u00b7{inner} = {e0}`.",
                "Do the two multiplications one at a time and write each result down before joining them.",
            )

        if p0 == e0:
            if p1 == 1:
                return (
                    "distribute_second_only",
                    f"You wrote `{ans}`. The {b} was multiplied correctly, but the `x` was left as plain `x`. "
                    f"The outside number multiplies every term in the bracket, including the `x`: `{a}\u00b7x = {a}x`.",
                    "Every term inside the bracket gets multiplied, including the one that is just `x`.",
                )
            return (
                "wrong_coefficient",
                f"You wrote `{ans}`. The number at the end is right, but in front of `x` you have `{p1}` instead of `{a}`. "
                f"The `x` inside the bracket is multiplied by {a}, so it becomes `{a}x`.",
                "Multiply the outside number by the `x`; the number in front of `x` should be exactly that outside number.",
            )

        return (
            "wrong_terms",
            f"You wrote `{ans}`, but neither term matches. `{q}` should give an `x` term and a number term, and each comes from its own multiplication: "
            f"`{a}\u00b7x` for the first and `{a}\u00b7{inner}` for the second.",
            "Split the problem into two small multiplications instead of doing it all at once.",
        )

    # (x+b)^2
    if p2 == 0:
        if p1 == 2 and p0 == 2 * b:
            return (
                "multiply_by_two",
                f"You wrote `{ans}`, as if the little `2` meant 'multiply by 2'. "
                f"An exponent of 2 means 'use the bracket twice': `(x+{b})^2 = (x+{b})(x+{b})`, which gives an `x^2` term.",
                "The exponent says how many times to write the bracket, not what to multiply by.",
            )
        if p1 == 0:
            return (
                "dropped_variable",
                f"Your answer `{ans}` is just a number, but `{q}` still has `x` in it once the bracket is removed. "
                "A single number is only right for one particular value of `x`, while the expansion has to work for every `x`.",
                "The expansion of a squared bracket with `x` in it always keeps an `x^2` term and an `x` term.",
            )
        return (
            "lost_square_term",
            f"Your answer `{ans}` has no `x^2`. `{q}` means `(x+{b})(x+{b})`, and the first terms of the two brackets multiply to give `x\u00b7x = x^2`, so it has to appear.",
            "Squared bracket in, `x^2` out. If your answer has no `x^2`, something was dropped.",
        )

    if p2 == 1:
        if p1 == 0 and p0 == b * b:
            return (
                "square_each_term",
                f"You wrote `{ans}`, which squares each term on its own: `x^2` and `{b}^2 = {b*b}`. "
                f"But `{q}` is the whole bracket multiplied by itself, and that creates a middle term which squaring term by term skips.",
                "Squaring doesn't pass through a plus sign. Always write the bracket twice and multiply.",
            )
        if p1 == b and p0 == b * b:
            return (
                "middle_term_not_doubled",
                f"You wrote `{ans}`. The `x^2` and the {b*b} are right, but the middle term should be `{2*b}x`, not `{b}x`. "
                f"It appears twice: `x\u00b7{b}` from one pair and `{b}\u00b7x` from the other, and `{b}x + {b}x = {2*b}x`.",
                "The middle term of a squared bracket always comes twice. Remember to add both copies.",
            )
        if p1 == 2 * b:
            return (
                "last_term_not_squared",
                f"You wrote `{ans}`. The `x^2` and the middle term `{2*b}x` are right, but the last term is `{p0}` instead of `{b*b}`. "
                f"The last term comes from the two numbers multiplying each other: `{b}\u00b7{b} = {b*b}`.",
                "The last term is the second number times itself, which is the same as squaring it.",
            )

    return (
        "wrong_terms",
        f"You wrote `{ans}`, but some terms don't match. `{q}` expands to three terms: `x^2`, a middle `x` term and a number, "
        f"and each one comes from multiplying a pair of terms from the two brackets.",
        "Write the bracket twice and multiply every term in the first by every term in the second. That gives four products, then combine like terms.",
    )


def explain_mistake(question, answer):
    """Full, specific explanation of why `answer` is wrong for `question`."""
    data = parse_expression(question)
    ans = str(answer).strip().replace("`", "")

    label, summary, tip = _classify(
        data, str(question), ans, parse_polynomial(answer)
    )

    return {
        "label": label,
        "title": ALL_LABELS.get(label, label),
        "summary": summary,
        "steps": worked_steps(data),
        "check": _quick_check(data, ans),
        "tip": tip,
    }


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
        ALL_LABELS.get(label, "Review this step of the expansion."),
    )


_KEY_BY_NAME = {name: key for key, name in ALL_LABELS.items()}

_PLUS = {"distribute_first_only", "distribute_second_only", "added_instead_of_multiplied"}
_SQUARE = {
    "square_each_term", "multiply_by_two", "middle_term_not_doubled",
    "last_term_not_squared", "lost_square_term",
}


def generate_question(misconception=None):
    a = random.randint(2, 9)
    b = random.randint(2, 9)

    key = _KEY_BY_NAME.get(misconception, misconception)

    if key in _PLUS:
        return f"{a}(x+{b})"

    if key == "ignore_minus_sign":
        return f"{a}(x-{b})"

    if key in _SQUARE:
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