import pandas as pd
from model import build_data, train, features

df = build_data()
held_out = "multiply_by_two"            # the misconception we hide from the model

train_df = df[df.label != held_out]
test_df = df[df.label == held_out]

model = train(train_df)
X = [features(r.question, r.answer, r.a, r.b) for r in test_df.itertuples()]
print("Model guesses for the misconception it never saw:")
print(pd.Series(model.predict(X)).value_counts())