import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix, classification_report
import os

base_dir = "/Users/subhiksharaj/Downloads/files (3)/subhicloudeproject"
df = pd.read_csv(os.path.join(base_dir, "dataset.csv"))

X = df[["score", "time_taken", "attempts"]]
y = df["skill_level"]

le = LabelEncoder()
y_encoded = le.fit_transform(y)

X_train, X_test, y_train, y_test = train_test_split(X, y_encoded, test_size=0.2, random_state=42)

model = DecisionTreeClassifier(max_depth=5, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)

labels = le.inverse_transform([0, 1, 2])
cm = confusion_matrix(y_test, y_pred)

print("Labels:", labels)
print("Confusion Matrix:\n", cm)
print("\nClassification Report:\n", classification_report(y_test, y_pred, target_names=labels))
