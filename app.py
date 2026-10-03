import re
import streamlit as st
from model import build_data, train, features

LABEL_NAMES = {
    "distribute_first_only": "Distributing to only the first term",
    "ignore_minus_sign": "Ignoring the minus sign when distributing",
    "square_each_term": "Squaring each term separately",
    "multiply_by_two": "Treating the square as 'multiply by 2'",
}

# Person B: improve these lesson texts
LESSONS = {
    "distribute_first_only": "The number outside the bracket multiplies EVERY term inside, not just the first. Test it: 2(x+3) with x=1 is 2 x 4 = 8. The answer 2x+3 gives 5, which is wrong. 2x+6 gives 8, which is right.",
    "ignore_minus_sign": "The minus sign stays attached to the number after it. 2(x-3) means 2x - 2x3 = 2x - 6. Test it with x=5: 2(5-3) = 4, and 2x-6 gives 4, but 2x+6 gives 16.",
    "square_each_term": "(x+3)^2 means (x+3) times (x+3), so you must multiply everything by everything: x*x + x*3 + 3*x + 3*3 = x^2 + 6x + 9. There is a middle term you can't skip. Test it with x=1: 4^2 = 16, and x^2+9 gives 10.",
    "multiply_by_two": "Squaring is not the same as doubling. (x+3)^2 means (x+3) times (x+3), not 2 times (x+3). Test it with x=1: (1+3)^2 = 16, but 2x+6 gives 8.",
}

RETESTS = {
    "distribute_first_only": ["4(x+5)", "3(x+7)", "6(x+2)"],
    "ignore_minus_sign": ["5(x-2)", "3(x-4)", "2(x-8)"],
    "square_each_term": ["(x+4)^2", "(x+5)^2", "(x+2)^2"],
    "multiply_by_two": ["(x+6)^2", "(x+1)^2", "(x+3)^2"],
}

QUESTIONS = ["2(x+3)", "5(x-4)", "(x+3)^2", "3(x+6)", "4(x-2)", "(x+5)^2"]


@st.cache_resource
def get_model():
    return train(build_data())


def norm(s):
    return s.replace(" ", "").lower().replace("²", "^2")


def parse(q):
    m = re.match(r"(\d+)\(x([+-])(\d+)\)$", q)
    if m:
        return int(m.group(1)), int(m.group(3))
    m = re.match(r"\(x\+(\d+)\)\^2$", q)
    return 5, int(m.group(1))


def correct_answer(q):
    a, b = parse(q)
    if "^2" in q:
        return f"x^2+{2*b}x+{b*b}"
    if "-" in q:
        return f"{a}x-{a*b}"
    return f"{a}x+{a*b}"


def diagnose(q, ans):
    a, b = parse(q)
    return get_model().predict([features(q, norm(ans), a, b)])[0]


s = st.session_state
s.setdefault("stage", "input")
s.setdefault("history", {})  # label -> {"seen": n, "resolved": n}

st.title("Re:Learn - Algebra Misconception Tutor")

# Learner model in the sidebar
st.sidebar.header("Learner history")
for lab, rec in s.history.items():
    st.sidebar.write(f"{LABEL_NAMES[lab]}: seen {rec['seen']}x, resolved {rec['resolved']}x")

if s.stage == "input":
    q = st.selectbox("Expand this expression:", QUESTIONS)
    ans = st.text_input("Your answer (example: 2x+6)")
    if st.button("Submit") and ans:
        if norm(ans) == correct_answer(q):
            s.stage = "correct"
        else:
            label = diagnose(q, ans)
            s.q, s.ans = q, ans
            if label == "correct":
                s.stage = "unknown"
            else:
                s.label = label
                rec = s.history.setdefault(label, {"seen": 0, "resolved": 0})
                rec["seen"] += 1
                s.stage = "lesson"
        st.rerun()

elif s.stage == "correct":
    st.success("Correct! Well done.")
    if st.button("Try another"):
        s.stage = "input"
        st.rerun()

elif s.stage == "unknown":
    st.warning(f"Your answer {s.ans} is not correct, but I can't tell which misconception caused it. I'm not confident enough to diagnose it.")
    st.info(f"The correct answer is {correct_answer(s.q)}.")
    if st.button("Try another"):
        s.stage = "input"
        st.rerun()

elif s.stage == "lesson":
    st.error(f"Your answer {s.ans} is not correct.")
    st.subheader(f"Diagnosis: {LABEL_NAMES[s.label]}")
    st.write(LESSONS[s.label])
    if st.button("I'm ready for the retest"):
        s.stage = "retest"
        st.rerun()

elif s.stage == "retest":
    st.subheader("Retest: all 3 must be right")
    answers = [st.text_input(f"Expand {q}", key=f"rt{i}") for i, q in enumerate(RETESTS[s.label])]
    if st.button("Check my answers"):
        right = sum(norm(a) == correct_answer(q) for a, q in zip(answers, RETESTS[s.label]))
        if right == 3:
            s.history[s.label]["resolved"] += 1
            s.stage = "resolved"
        else:
            s.stage = "again"
            s.right = right
        st.rerun()

elif s.stage == "resolved":
    st.success(f"Misconception resolved: {LABEL_NAMES[s.label]}. All 3 retest questions correct.")
    if st.button("Start over"):
        s.stage = "input"
        st.rerun()

elif s.stage == "again":
    st.warning(f"Only {s.right}/3 correct, so the misconception is NOT yet resolved. Review the lesson again.")
    st.write(LESSONS[s.label])
    if st.button("Retry the retest"):
        s.stage = "retest"
        st.rerun()