# 🧠 Re:Learn

### Learn from the mistake, not just the answer.

**Re:Learn** is an interactive algebra learning application built with **Python and Streamlit**. Instead of simply marking an answer as right or wrong, Re:Learn identifies the **misconception behind an incorrect answer**, explains what went wrong, and gives the learner targeted questions to prove that the concept has been understood.

---

## 🎯 Problem

Traditional learning systems often tell students:

> ❌ Wrong answer.

But they don't always explain **why** the answer was wrong.

For example:

```text
2(x + 3)

Student: 2x + 3
Correct:  2x + 6
```

The important information is not just that the answer is incorrect.

The student has made a specific misconception:

**"Only distributing to the first term."**

Re:Learn focuses on identifying and fixing that misconception.

---

## 💡 Solution

Re:Learn follows a simple learning loop:

```text
              ┌─────────────────┐
              │     PRACTICE    │
              │                 │
              │ Choose /        │
              │ Generate /      │
              │ Write question  │
              └────────┬────────┘
                       │
                       ▼
              ┌─────────────────┐
              │  SOLVE QUESTION │
              │                 │
              │ Student submits │
              │ an answer       │
              └────────┬────────┘
                       │
                ┌──────┴──────┐
                │             │
             Correct        Wrong
                │             │
                ▼             ▼
        ┌─────────────┐ ┌─────────────────┐
        │   PROGRESS  │ │   DIAGNOSE      │
        │    SAVED    │ │   MISCONCEPTION │
        └─────────────┘ └────────┬────────┘
                                 │
                                 ▼
                       ┌─────────────────┐
                       │    EXPLAIN      │
                       │   THE MISTAKE   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  3-QUESTION     │
                       │     RETEST      │
                       └────────┬────────┘
                                │
                         ┌──────┴──────┐
                         │             │
                       3/3           < 3/3
                         │             │
                         ▼             ▼
                  ┌────────────┐ ┌────────────┐
                  │   CONCEPT  │ │   RETRY /  │
                  │  RESOLVED  │ │   LEARN    │
                  └────────────┘ └──────┬─────┘
                                        │
                                        └──────► Retest
```

---

## ✨ Features

### 📚 Multiple Practice Modes

Users can practice through:

- **Question Bank**
- **Generated Questions**
- **Practice Weak Areas**
- **Write My Own Question**

The application supports algebra expressions such as:

```text
2(x+3)
5(x-4)
(x+3)^2
```

Questions can also be generated specifically around a learner's previously identified misconception.

---

### 🔍 Misconception Diagnosis

When an answer is incorrect, Re:Learn doesn't stop at "wrong."

It analyzes the response and identifies errors such as:

- Only distributing to the first term
- Losing the minus sign
- Missing the middle term when squaring
- Treating a square like multiplication by 2
- Dropping the variable
- Wrong coefficient
- Wrong constant
- Extra square term
- Incorrect or unreadable expressions

The engine contains both deterministic checks and structured misconception categories.

---

### 🧑‍🏫 Step-by-Step Explanation

After diagnosing a mistake, Re:Learn explains the mathematical step that caused the error.

For example:

```text
2(x + 3)

2 × x = 2x
2 × 3 = 6

Therefore:

2(x + 3) = 2x + 6
```

The explanation engine provides worked steps for distribution, negative signs, and squaring expressions.

---

### 🎯 Targeted Retesting

After a misconception is identified, Re:Learn generates **three fresh questions based on the same misconception**.

The learner must answer all three correctly to mark the concept as resolved.

```text
Mistake
   ↓
Explanation
   ↓
3 Targeted Questions
   ↓
 ┌───────────────┐
 │     3 / 3     │ ──► Concept Resolved ✓
 └───────────────┘
        │
        └──────────► Otherwise → Keep Practicing
```

The app records a resolution only when all three retest questions are answered correctly.

---

### 📊 Progress Tracking

Re:Learn stores learning activity locally and tracks:

- Total attempts
- Correct answers
- Accuracy
- Resolved misconceptions
- Current streak
- Attempts per misconception
- Resolution rate

This allows the learner to see **what they are improving at and where they still struggle**.

---

## 📸 Application Screenshots

### 🏠 Home Page

<img width="859" height="400" alt="Screenshot 2026-10-04 123747" src="https://github.com/user-attachments/assets/f431ab92-2e9e-4f84-b16b-4ca10fe32c0d" />


---

### 📝 Practice Page

<img width="859" height="407" alt="Screenshot 2026-10-04 123800" src="https://github.com/user-attachments/assets/88c73d5f-758b-490e-bc69-99387debacb9" />

---

### 🔍 Wrong Answer Explanation

<img width="762" height="568" alt="Screenshot 2026-10-04 123827" src="https://github.com/user-attachments/assets/d3cdf6e9-489d-4ece-b943-0b87640700d5" />


---

## 🏗️ Architecture

```text
                    ┌──────────────────┐
                    │    Streamlit UI  │
                    │      app.py      │
                    └────────┬─────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
       ┌────────────┐ ┌────────────┐ ┌────────────┐
       │   ui.py    │ │  engine.py │ │   db.py    │
       │            │ │            │ │            │
       │ UI / Theme │ │ Algebra &  │ │ Persistence│
       │ Components │ │ Diagnosis  │ │ & Progress │
       └────────────┘ └────────────┘ └──────┬─────┘
                                            │
                                            ▼
                                    ┌──────────────┐
                                    │  relearn.db  │
                                    │    SQLite    │
                                    └──────────────┘
```

---

## 📁 File Structure

```text
ReLearn/
│
├── app.py          # Main Streamlit application and navigation
├── engine.py       # Algebra engine, answer checking and diagnosis
├── db.py           # SQLite database and progress tracking
├── ui.py           # UI components and custom styling
├── relearn.db      # Local SQLite database
├── README.md       # Project documentation
│
└── images/
    ├── home.png
    ├── practice.png
    └── explanation.png
```

---

## 🧠 How Answer Checking Works

Re:Learn normalizes student answers and evaluates mathematical equivalence.

Instead of relying only on string comparison, the engine evaluates expressions for multiple values of `x`.

```text
Student Answer
      │
      ▼
Normalize Expression
      │
      ▼
Evaluate for multiple x values
      │
      ▼
Compare with Correct Expression
      │
 ┌────┴────┐
 │         │
Same      Different
 │         │
 ▼         ▼
Correct   Diagnose
```

This allows mathematically equivalent expressions to be accepted even if they are written differently.

---

## 🤖 Machine Learning Component

The project also contains a **Random Forest classifier** for misconception classification.

Training data is generated synthetically for different algebra mistake categories, and the model uses features such as:

- Question type
- Coefficient
- Constant
- Presence of `x²`
- Sign information
- Expected coefficient/constant relationships

The Random Forest is configured with **160 estimators**, balanced class weights, and a maximum depth of 12.

The current application primarily uses the rule-based explanation/diagnosis pipeline for producing the learner-facing explanation.

---

## 🗄️ Database

Re:Learn uses **SQLite** for local persistence.

The database contains:

### `users`

Stores learner profiles.

### `attempts`

Stores:

```text
Question
User Answer
Correct Answer
Misconception
Confidence
Correct / Incorrect
Timestamp
```

### `resolutions`

Stores misconceptions successfully resolved through retesting.

---

## 🎨 User Interface

The interface is built using **Streamlit** with a custom CSS theme.

The UI includes:

- Learner profile
- Home dashboard
- Practice interface
- Answer checking
- Misconception diagnosis
- Retest screen
- Progress dashboard
- Responsive styling

---

## 🛠️ Tech Stack

| Technology | Purpose |
|---|---|
| Python | Core application |
| Streamlit | Interactive web UI |
| SQLite | Local data storage |
| Scikit-learn | Random Forest classifier |
| HTML/CSS | Custom interface styling |

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone <your-repository-url>
cd ReLearn
```

### 2. Install dependencies

```bash
pip install streamlit pandas scikit-learn
```

### 3. Run the application

```bash
streamlit run app.py
```

The application will open in your browser.

---

## 🎮 Demo Flow

For a quick demonstration:

```text
1. Create Profile
       ↓
2. Go to Practice
       ↓
3. Choose a question
       ↓
4. Enter an incorrect answer
       ↓
5. Re:Learn identifies the misconception
       ↓
6. Read the explanation
       ↓
7. Start 3-question retest
       ↓
8. Resolve the misconception
       ↓
9. View progress
```

---

## 🧪 Example Demo

Try:

```text
Question:
2(x+3)

Wrong answer:
2x+3
```

Re:Learn identifies:

```text
Only distributing to the first term
```

Then it explains:

```text
2 × x = 2x
2 × 3 = 6

Correct answer:
2x + 6
```

Finally, it generates three similar questions to check whether the learner has actually understood the concept.

---

## 🌟 What Makes Re:Learn Different?

Most educational systems follow:

```text
Question → Answer → Right/Wrong
```

Re:Learn follows:

```text
Question
   ↓
Answer
   ↓
Understand WHY
   ↓
Identify Misconception
   ↓
Explain
   ↓
Targeted Practice
   ↓
Retest
   ↓
Concept Mastery
```

**The goal isn't just to get the current question right.**

**The goal is to fix the underlying misconception.**

---

## 🔮 Future Scope

Possible future improvements include:

- More algebra topics
- More sophisticated misconception detection
- Larger training datasets
- Adaptive difficulty
- Personalized learning paths
- Teacher dashboards
- Cloud-based learner profiles
- More detailed learning analytics
- Support for additional mathematical notation

---

## 👥 Project

**Re:Learn — An Adaptive Algebra Learning Assistant**

Built to demonstrate how learning systems can move beyond simply detecting incorrect answers and instead help learners understand and correct the reasoning behind their mistakes.

---

### Made with ❤️, Python, and a lot of algebra.
