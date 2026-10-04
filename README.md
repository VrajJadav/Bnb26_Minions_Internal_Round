[README.md](https://github.com/user-attachments/files/33016749/README.md)
# Re:Learn - Algebra Misconception Tutor

Bit N Build (GDG FRCRCE) - AI/ML Problem Statement 3

## What it does
Instead of marking an answer "wrong", Re:Learn diagnoses WHICH misconception
caused it, shows a targeted lesson, then retests the student. A misconception
is marked resolved only when all 3 new retest questions are answered correctly.

## Misconceptions covered (expanding brackets)
1. Distributing to only the first term: 2(x+3) -> 2x+3
2. Ignoring the minus sign: 2(x-3) -> 2x+6
3. Squaring each term separately: (x+3)^2 -> x^2+9
4. Treating a square as "multiply by 2": (x+3)^2 -> 2x+6

## How it works
- model.py: generates labelled wrong answers with code, trains a random forest,
  prints accuracy and a confusion matrix
- unseen.py: hides one misconception from training to test generalisation
- app.py: Streamlit app (diagnosis, lesson, retest, learner history)

## Install
pip3 install pandas scikit-learn streamlit

## Run
python3 model.py
python3 -m streamlit run app.py

## Limitations
- Data is synthetic, so accuracy is higher than it would be on real student work
- The model can only name misconceptions it was trained on
- Only one topic (expanding brackets) is covered
- Future work: test on real student answers and add an "unknown" option
