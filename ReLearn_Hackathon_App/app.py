import streamlit as st

from db import (
    init_database,
    create_or_get_user,
    get_user_by_id,
    get_user_stats,
    get_misconception_stats,
    save_attempt,
    save_resolution,
)
from engine import (
    check_answer,
    diagnose_mistake,
    get_lesson,
    generate_question,
    get_retest_questions,
    validate_question,
)
from ui import (
    apply_theme,
    render_login,
    render_sidebar_profile,
    render_header,
    render_dashboard,
    render_diagnosis,
)

st.set_page_config(
    page_title="Re:Learn",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_theme()
init_database()

DEFAULTS = {
    "user_id": None,
    "username": None,
    "initials": None,
    "page": "home",
    "question": None,
    "source": None,
    "answer": "",
    "diagnosis": None,
    "confidence": 0,
    "retest_questions": [],
    "retest_result": None,
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def load_user(user):
    st.session_state.user_id = user["id"]
    st.session_state.username = user["name"]
    st.session_state.initials = user["initials"]


# ------------------------------------------------------------
# RESTORE USER FROM URL
# ------------------------------------------------------------

if st.session_state.user_id is None:
    user_id_from_url = st.query_params.get("user")
    if user_id_from_url:
        user = get_user_by_id(user_id_from_url)
        if user:
            load_user(user)


# ------------------------------------------------------------
# LOGIN / PROFILE CREATION
# ------------------------------------------------------------

if st.session_state.user_id is None:
    render_login()

    name = st.text_input(
        "Your name",
        placeholder="e.g. Madhura Apraj",
        label_visibility="collapsed",
    )

    if st.button(
        "Create my profile  →",
        type="primary",
        use_container_width=True,
    ):
        if not name.strip():
            st.warning("Please enter your name.")
        else:
            user = create_or_get_user(name)
            load_user(user)
            st.query_params["user"] = user["id"]
            st.rerun()

    st.caption("Your profile is stored locally for this hackathon demo.")
    st.stop()


user_id = st.session_state.user_id
username = st.session_state.username
initials = st.session_state.initials


# ------------------------------------------------------------
# SIDEBAR
# ------------------------------------------------------------

with st.sidebar:
    render_sidebar_profile(username, initials, user_id)

    st.divider()

    nav = {
        "🏠  Home": "home",
        "🎯  Practice": "practice",
        "📊  My Progress": "progress",
    }

    for label, page in nav.items():
        if st.button(
            label,
            use_container_width=True,
            type="secondary" if st.session_state.page != page else "primary",
        ):
            st.session_state.page = page
            if page == "practice":
                st.session_state.question = None
            st.rerun()

    st.divider()

    if st.button("Sign out", use_container_width=True):
        st.query_params.clear()
        for key, value in DEFAULTS.items():
            st.session_state[key] = value
        st.rerun()


# ------------------------------------------------------------
# HOME
# ------------------------------------------------------------

if st.session_state.page == "home":
    render_header(username, initials)

    stats = get_user_stats(user_id)
    render_dashboard(stats)

    st.markdown("### How Re:Learn works")

    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-number">01</div>
            <h3>Practice</h3>
            <p>Choose a question, generate one automatically, or write your own.</p>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-number">02</div>
            <h3>Understand</h3>
            <p>Re:Learn identifies the misconception behind an incorrect answer.</p>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-number">03</div>
            <h3>Improve</h3>
            <p>Learn the concept and prove it through targeted retesting.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("###")

    if st.button(
        "Start practicing  →",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.page = "practice"
        st.rerun()


# ------------------------------------------------------------
# PRACTICE
# ------------------------------------------------------------

elif st.session_state.page == "practice":
    render_header(username, initials)

    st.markdown('<div class="eyebrow">PRACTICE</div>', unsafe_allow_html=True)
    st.markdown("## Choose your practice mode")
    st.caption("Build your algebra skills one misconception at a time.")

    option = st.radio(
        "Practice mode",
        [
            "Question Bank",
            "Generate a Question",
            "Practice Weak Area",
            "Write My Own",
        ],
        horizontal=True,
        label_visibility="collapsed",
    )

    if option == "Question Bank":
        questions = [
            "2(x+3)", "5(x-4)", "3(x+6)",
            "4(x-2)", "7(x+2)", "6(x-3)",
            "(x+3)^2", "(x+5)^2", "(x+7)^2",
        ]

        question = st.selectbox("Select a question", questions)

        if st.button("Use this question  →", type="primary"):
            st.session_state.question = question
            st.session_state.source = "Question Bank"
            st.session_state.page = "answer"
            st.rerun()

    elif option == "Generate a Question":
        st.info("Re:Learn will generate a fresh algebra problem.")

        if st.button("Generate question  →", type="primary"):
            st.session_state.question = generate_question()
            st.session_state.source = "Generated"
            st.session_state.page = "answer"
            st.rerun()

    elif option == "Practice Weak Area":
        stats = get_misconception_stats(user_id)

        if not stats:
            st.info("Complete a few questions first. Your weak areas will appear here.")
            if st.button("Generate a normal question", type="primary"):
                st.session_state.question = generate_question()
                st.session_state.source = "Generated"
                st.session_state.page = "answer"
                st.rerun()
        else:
            labels = [item["label"] for item in stats]
            selected = st.selectbox("Choose a misconception", labels)

            if st.button("Practice this weakness  →", type="primary"):
                st.session_state.question = generate_question(selected)
                st.session_state.source = "Weak Area"
                st.session_state.page = "answer"
                st.rerun()

    else:
        custom = st.text_input(
            "Expression",
            placeholder="Example: 8(x-3) or (x+6)^2",
        )

        if st.button("Use my question  →", type="primary"):
            valid, message = validate_question(custom)
            if valid:
                st.session_state.question = custom.strip()
                st.session_state.source = "Custom"
                st.session_state.page = "answer"
                st.rerun()
            else:
                st.error(message)


# ------------------------------------------------------------
# ANSWER
# ------------------------------------------------------------

elif st.session_state.page == "answer":
    question = st.session_state.question

    if not question:
        st.session_state.page = "practice"
        st.rerun()

    render_header(username, initials)

    st.markdown(f"""
    <div class="question-box">
        <div class="question-label">YOUR QUESTION</div>
        <div class="question-text">{question}</div>
    </div>
    """, unsafe_allow_html=True)

    answer = st.text_input(
        "Your answer",
        placeholder="Example: 2x+6",
    )

    st.caption("You can write 2x+6, 2x-6, x^2+6x+9, etc.")

    c1, c2 = st.columns(2)

    with c1:
        if st.button("← Choose another", use_container_width=True):
            st.session_state.page = "practice"
            st.session_state.question = None
            st.rerun()

    with c2:
        if st.button(
            "Check answer  →",
            type="primary",
            use_container_width=True,
        ):
            if not answer.strip():
                st.warning("Please enter your answer.")
            else:
                is_correct, correct = check_answer(question, answer)

                if is_correct:
                    save_attempt(
                        user_id, question, answer, correct,
                        None, 100, True
                    )
                    st.session_state.page = "correct"
                else:
                    label, confidence = diagnose_mistake(question, answer)

                    save_attempt(
                        user_id, question, answer, correct,
                        label, confidence, False
                    )

                    st.session_state.answer = answer
                    st.session_state.diagnosis = label
                    st.session_state.confidence = confidence
                    st.session_state.page = "diagnosis"

                st.rerun()


# ------------------------------------------------------------
# CORRECT
# ------------------------------------------------------------

elif st.session_state.page == "correct":
    render_header(username, initials)

    st.markdown("""
    <div class="result-card success-card">
        <div class="success-icon">✓</div>
        <div class="eyebrow success-text">PROGRESS SAVED</div>
        <h2>That's correct.</h2>
        <p>Your answer is mathematically equivalent to the original expression.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        if st.button("Try another question", type="primary", use_container_width=True):
            st.session_state.page = "practice"
            st.session_state.question = None
            st.rerun()

    with c2:
        if st.button("View my progress", use_container_width=True):
            st.session_state.page = "progress"
            st.rerun()


# ------------------------------------------------------------
# DIAGNOSIS
# ------------------------------------------------------------

elif st.session_state.page == "diagnosis":
    question = st.session_state.question
    answer = st.session_state.answer
    label = st.session_state.diagnosis
    confidence = st.session_state.confidence

    render_header(username, initials)

    st.markdown("""
    <div class="wrong-banner">
        <div class="wrong-title">Not quite.</div>
        <div class="wrong-subtitle">Let's understand the step that caused the error.</div>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2)

    with c1:
        st.markdown("**Your answer**")
        st.code(answer, language="text")

    with c2:
        st.markdown("**Correct answer**")
        from engine import get_correct_answer
        st.code(get_correct_answer(question), language="text")

    render_diagnosis(
        label,
        confidence,
        get_lesson(label, question),
    )

    st.markdown("### Ready to practice this specific mistake?")

    if st.button(
        "Start 3-question retest  →",
        type="primary",
        use_container_width=True,
    ):
        st.session_state.retest_questions = get_retest_questions(label)
        st.session_state.page = "retest"
        st.rerun()


# ------------------------------------------------------------
# RETEST
# ------------------------------------------------------------

elif st.session_state.page == "retest":
    label = st.session_state.diagnosis

    render_header(username, initials)

    st.markdown('<div class="eyebrow">RETEST</div>', unsafe_allow_html=True)
    st.markdown("## Let's see if the concept stuck.")
    st.caption("Three fresh questions based on the same misconception.")

    questions = st.session_state.retest_questions
    answers = []

    for i, question in enumerate(questions):
        st.markdown(f"#### {i + 1}. `{question}`")
        answers.append(
            st.text_input(
                "Your answer",
                key=f"retest_answer_{i}",
            )
        )

    if st.button("Check retest  →", type="primary", use_container_width=True):
        right = 0

        for question, answer in zip(questions, answers):
            if answer.strip() and check_answer(question, answer)[0]:
                right += 1

        st.session_state.retest_result = right

        if right == 3:
            save_resolution(user_id, label)
            st.session_state.page = "resolved"
        else:
            st.session_state.page = "retry"

        st.rerun()


# ------------------------------------------------------------
# RESOLVED
# ------------------------------------------------------------

elif st.session_state.page == "resolved":
    render_header(username, initials)

    st.markdown("""
    <div class="result-card success-card">
        <div class="success-icon">✓</div>
        <div class="eyebrow success-text">CONCEPT RESOLVED</div>
        <h2>You've got it.</h2>
        <p>You answered all three retest questions correctly.</p>
    </div>
    """, unsafe_allow_html=True)

    if st.button("Continue practicing  →", type="primary", use_container_width=True):
        st.session_state.page = "practice"
        st.session_state.question = None
        st.rerun()


# ------------------------------------------------------------
# RETRY
# ------------------------------------------------------------

elif st.session_state.page == "retry":
    right = st.session_state.retest_result
    label = st.session_state.diagnosis

    render_header(username, initials)

    st.markdown("""
    <div class="result-card retry-card">
        <h2>Keep going.</h2>
        <p>You're learning the exact step that caused the mistake.</p>
    </div>
    """, unsafe_allow_html=True)

    st.warning(f"You got {right}/3 correct.")
    st.write(get_lesson(label, st.session_state.question))

    if st.button("Try another retest  →", type="primary", use_container_width=True):
        st.session_state.retest_questions = get_retest_questions(label)
        st.session_state.page = "retest"
        st.rerun()


# ------------------------------------------------------------
# PROGRESS
# ------------------------------------------------------------

elif st.session_state.page == "progress":
    render_header(username, initials)

    st.markdown('<div class="eyebrow">YOUR PROFILE</div>', unsafe_allow_html=True)
    st.markdown("## Learning progress")

    stats = get_user_stats(user_id)
    render_dashboard(stats, detailed=True)

    misconception_stats = get_misconception_stats(user_id)

    if misconception_stats:
        st.markdown("### Learning patterns")

        for item in misconception_stats:
            st.markdown(f"""
            <div class="progress-row">
                <div>
                    <b>{item['label']}</b>
                    <br>
                    <span class="muted">{item['attempts']} diagnosed attempts</span>
                </div>
                <div class="progress-percent">
                    {item['resolution_rate']}%
                    <small>resolved</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("Your misconception patterns will appear here after you make some attempts.")

    if st.button("Practice again  →", type="primary", use_container_width=True):
        st.session_state.page = "practice"
        st.session_state.question = None
        st.rerun()
