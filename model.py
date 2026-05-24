# ═══════════════════════════════════════════════════════════════════════════════
# ML Model + Intelligent Dataset Insight Engine
# ═══════════════════════════════════════════════════════════════════════════════
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.preprocessing import LabelEncoder
import os

model = None
le = None
dataset_stats = None  # Cached dataset statistics


# ─── Training ───────────────────────────────────────────────────────────────────

def train_model():
    global model, le, dataset_stats
    base_dir = os.path.dirname(os.path.abspath(__file__))
    df = pd.read_csv(os.path.join(base_dir, "dataset.csv"))

    X = df[["score", "time_taken", "attempts"]]
    y = df["skill_level"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = DecisionTreeClassifier(max_depth=5, random_state=42)
    model.fit(X, y_encoded)

    # Pre-compute dataset statistics
    dataset_stats = _compute_stats(df)


def _compute_stats(df):
    """Extract comprehensive dataset statistics for comparison and insights."""
    stats = {
        "total_records": len(df),
        "score": {
            "mean": round(float(df["score"].mean()), 1),
            "median": round(float(df["score"].median()), 1),
            "min": int(df["score"].min()),
            "max": int(df["score"].max()),
            "std": round(float(df["score"].std()), 1),
        },
        "time_taken": {
            "mean": round(float(df["time_taken"].mean()), 1),
            "median": round(float(df["time_taken"].median()), 1),
            "min": int(df["time_taken"].min()),
            "max": int(df["time_taken"].max()),
            "std": round(float(df["time_taken"].std()), 1),
        },
        "attempts": {
            "mean": round(float(df["attempts"].mean()), 1),
            "median": round(float(df["attempts"].median()), 1),
            "min": int(df["attempts"].min()),
            "max": int(df["attempts"].max()),
            "std": round(float(df["attempts"].std()), 1),
        },
        "skill_distribution": df["skill_level"].value_counts().to_dict(),
        # Per-skill averages for comparison
        "by_skill": {},
    }
    for skill in ["Beginner", "Intermediate", "Advanced"]:
        subset = df[df["skill_level"] == skill]
        if len(subset) > 0:
            stats["by_skill"][skill] = {
                "avg_score": round(float(subset["score"].mean()), 1),
                "avg_time": round(float(subset["time_taken"].mean()), 1),
                "avg_attempts": round(float(subset["attempts"].mean()), 1),
                "count": len(subset),
            }
    return stats


# ─── Prediction ─────────────────────────────────────────────────────────────────

def predict_skill(score, time_taken, attempts):
    global model, le
    if model is None:
        train_model()
    features = [[score, time_taken, attempts]]
    pred = model.predict(features)
    proba = model.predict_proba(features)
    skill_level = le.inverse_transform(pred)[0]
    confidence = round(max(proba[0]) * 100, 1)
    return skill_level, confidence


# ─── Explainable AI ─────────────────────────────────────────────────────────────

def explain_prediction(score, time_taken, attempts, skill_level):
    """Generate human-readable explanation of WHY the model made this prediction."""
    reasons = []
    stats = get_dataset_stats()

    # Score reasoning
    if score >= 80:
        reasons.append({"factor": "Score", "value": score, "verdict": "High",
                        "detail": "Your score is in the top tier, indicating strong subject mastery.",
                        "icon": "🏆", "impact": "positive"})
    elif score >= 55:
        reasons.append({"factor": "Score", "value": score, "verdict": "Moderate",
                        "detail": "Your score is average — you understand the basics but have room to grow.",
                        "icon": "📊", "impact": "neutral"})
    else:
        reasons.append({"factor": "Score", "value": score, "verdict": "Low",
                        "detail": "Your score suggests foundational gaps. Focus on core concepts first.",
                        "icon": "📚", "impact": "negative"})

    # Time reasoning
    if time_taken <= 20:
        reasons.append({"factor": "Speed", "value": f"{time_taken}min", "verdict": "Fast",
                        "detail": "You completed this quickly — a sign of confidence and readiness.",
                        "icon": "⚡", "impact": "positive"})
    elif time_taken <= 40:
        reasons.append({"factor": "Speed", "value": f"{time_taken}min", "verdict": "Moderate",
                        "detail": "Your pace is normal. Neither rushed nor slow — solid approach.",
                        "icon": "⏱️", "impact": "neutral"})
    else:
        reasons.append({"factor": "Speed", "value": f"{time_taken}min", "verdict": "Slow",
                        "detail": "You took longer than average. Try breaking complex topics into smaller parts.",
                        "icon": "🐢", "impact": "negative"})

    # Attempts reasoning
    if attempts <= 1:
        reasons.append({"factor": "Accuracy", "value": f"{attempts} attempt", "verdict": "Excellent",
                        "detail": "First-try success! This shows deep understanding of the material.",
                        "icon": "🎯", "impact": "positive"})
    elif attempts <= 3:
        reasons.append({"factor": "Accuracy", "value": f"{attempts} attempts", "verdict": "Average",
                        "detail": "A few retries is normal. Review errors to reduce future attempts.",
                        "icon": "🔄", "impact": "neutral"})
    else:
        reasons.append({"factor": "Accuracy", "value": f"{attempts} attempts", "verdict": "Needs Work",
                        "detail": "High attempt count shows trial-and-error learning. Study theory before practicing.",
                        "icon": "⚠️", "impact": "negative"})

    # Build summary
    positive = sum(1 for r in reasons if r["impact"] == "positive")
    negative = sum(1 for r in reasons if r["impact"] == "negative")

    if skill_level == "Advanced":
        summary = f"You're classified as Advanced because all your metrics align with top performers in our dataset of {stats['total_records']} learners."
    elif skill_level == "Intermediate":
        summary = f"You fall into Intermediate because your performance is mixed — some strengths, some areas to improve — compared to {stats['total_records']} learners."
    else:
        summary = f"You're at Beginner level. Compared to {stats['total_records']} learners in our dataset, your metrics suggest you're still building foundational skills."

    return {"reasons": reasons, "summary": summary, "positive": positive, "negative": negative}


# ─── Dataset Comparison ─────────────────────────────────────────────────────────

def compare_with_dataset(score, time_taken, attempts):
    """Compare user input against dataset averages and generate conversational insights."""
    stats = get_dataset_stats()
    insights = []

    # Score comparison
    diff = score - stats["score"]["mean"]
    if diff > 15:
        insights.append({"icon": "🌟", "type": "above",
            "msg": f"Your score of {score} is {abs(diff):.0f} points above the dataset average ({stats['score']['mean']}). Outstanding performance!"})
    elif diff > 0:
        insights.append({"icon": "👍", "type": "above",
            "msg": f"Your score of {score} is slightly above average ({stats['score']['mean']}). You're on the right track!"})
    elif diff > -15:
        insights.append({"icon": "💪", "type": "below",
            "msg": f"Your score of {score} is close to the average ({stats['score']['mean']}). A little more effort and you'll be ahead!"})
    else:
        insights.append({"icon": "📖", "type": "below",
            "msg": f"Your score of {score} is {abs(diff):.0f} points below average ({stats['score']['mean']}). Don't worry — review the basics and you'll improve quickly."})

    # Time comparison
    diff_t = time_taken - stats["time_taken"]["mean"]
    if diff_t < -10:
        insights.append({"icon": "🚀", "type": "above",
            "msg": f"You finished in {time_taken}min — that's {abs(diff_t):.0f}min faster than the average ({stats['time_taken']['mean']}min). Impressive speed!"})
    elif diff_t < 0:
        insights.append({"icon": "⏱️", "type": "above",
            "msg": f"You finished in {time_taken}min, slightly faster than average ({stats['time_taken']['mean']}min). Good pace!"})
    elif diff_t < 10:
        insights.append({"icon": "🕐", "type": "below",
            "msg": f"You took {time_taken}min, slightly more than the average ({stats['time_taken']['mean']}min). Try to optimize your workflow."})
    else:
        insights.append({"icon": "⏳", "type": "below",
            "msg": f"At {time_taken}min, you took {abs(diff_t):.0f}min longer than average. Break tasks into smaller steps to improve speed."})

    # Attempts comparison
    diff_a = attempts - stats["attempts"]["mean"]
    if diff_a < -1:
        insights.append({"icon": "🎯", "type": "above",
            "msg": f"Only {attempts} attempt(s) — well below the average of {stats['attempts']['mean']}. You learn efficiently!"})
    elif diff_a <= 0:
        insights.append({"icon": "✅", "type": "above",
            "msg": f"{attempts} attempt(s) is right at the average ({stats['attempts']['mean']}). Solid consistency!"})
    elif diff_a < 2:
        insights.append({"icon": "🔁", "type": "below",
            "msg": f"You used {attempts} attempts, slightly above average ({stats['attempts']['mean']}). Review your errors before retrying."})
    else:
        insights.append({"icon": "📝", "type": "below",
            "msg": f"At {attempts} attempts, you're above the dataset average ({stats['attempts']['mean']}). Focus on understanding concepts before hands-on practice."})

    # Percentile ranking
    pct_score = min(99, max(1, int((score - stats["score"]["min"]) / max(1, stats["score"]["max"] - stats["score"]["min"]) * 100)))
    insights.append({"icon": "📊", "type": "stat",
        "msg": f"Your score puts you in the top {100 - pct_score}% of all learners in our dataset."})

    return insights


# ─── Improvement Suggestions ───────────────────────────────────────────────────

def get_improvement_suggestions(score, time_taken, attempts, skill_level):
    """Generate actionable improvement recommendations based on dataset patterns."""
    stats = get_dataset_stats()
    suggestions = []

    if skill_level == "Beginner":
        target = stats["by_skill"].get("Intermediate", {})
        suggestions.append({
            "icon": "🎯", "priority": "high",
            "msg": f"To reach Intermediate: aim for a score above {target.get('avg_score', 65)} (you have {score}).",
        })
        suggestions.append({
            "icon": "⏱️", "priority": "high",
            "msg": f"Try to complete tasks under {target.get('avg_time', 35)} minutes (you took {time_taken}min).",
        })
        suggestions.append({
            "icon": "🔄", "priority": "medium",
            "msg": f"Reduce attempts to {target.get('avg_attempts', 2.5):.0f} or fewer (you used {attempts}).",
        })
        suggestions.append({
            "icon": "📚", "priority": "medium",
            "msg": "Start with foundational tutorials. Watch a concept video before attempting labs.",
        })

    elif skill_level == "Intermediate":
        target = stats["by_skill"].get("Advanced", {})
        suggestions.append({
            "icon": "🏆", "priority": "high",
            "msg": f"To reach Advanced: push your score above {target.get('avg_score', 85)} (you have {score}).",
        })
        suggestions.append({
            "icon": "⚡", "priority": "high",
            "msg": f"Advanced learners average {target.get('avg_time', 18)}min. Try to cut your time from {time_taken}min.",
        })
        suggestions.append({
            "icon": "🎯", "priority": "medium",
            "msg": f"Advanced users average {target.get('avg_attempts', 1.0):.0f} attempt. Reduce retries by studying errors.",
        })
        suggestions.append({
            "icon": "🔬", "priority": "medium",
            "msg": "Try combining multiple cloud services in a mini-project to deepen understanding.",
        })

    else:  # Advanced
        suggestions.append({
            "icon": "💎", "priority": "low",
            "msg": "You're already performing at the highest level! Focus on optimization and teaching others.",
        })
        suggestions.append({
            "icon": "🏗️", "priority": "low",
            "msg": "Challenge yourself with multi-service architectures and real-world deployment scenarios.",
        })
        suggestions.append({
            "icon": "💰", "priority": "medium",
            "msg": "Focus on cost optimization — learn to achieve the same results with fewer resources.",
        })

    return suggestions


# ─── What-If Analysis ──────────────────────────────────────────────────────────

def what_if_analysis(score, time_taken, attempts):
    """Simulate changes and predict outcomes."""
    scenarios = []

    # Scenario 1: Better score
    if score < 90:
        new_score = min(95, score + 15)
        new_skill, new_conf = predict_skill(new_score, time_taken, attempts)
        scenarios.append({
            "change": f"Score increases from {score} → {new_score}",
            "icon": "📈",
            "result_skill": new_skill,
            "result_conf": new_conf,
            "detail": f"A {new_score - score} point boost would shift your prediction to {new_skill} ({new_conf}% confidence).",
        })

    # Scenario 2: Fewer attempts
    if attempts > 1:
        new_skill, new_conf = predict_skill(score, time_taken, 1)
        scenarios.append({
            "change": f"Attempts reduced from {attempts} → 1",
            "icon": "🎯",
            "result_skill": new_skill,
            "result_conf": new_conf,
            "detail": f"Completing on the first try would change your prediction to {new_skill} ({new_conf}% confidence).",
        })

    # Scenario 3: Faster time
    if time_taken > 20:
        new_time = max(15, time_taken - 15)
        new_skill, new_conf = predict_skill(score, new_time, attempts)
        scenarios.append({
            "change": f"Time reduced from {time_taken}min → {new_time}min",
            "icon": "⏱️",
            "result_skill": new_skill,
            "result_conf": new_conf,
            "detail": f"Saving {time_taken - new_time} minutes would change your prediction to {new_skill} ({new_conf}% confidence).",
        })

    # Scenario 4: Combined improvement
    best_skill, best_conf = predict_skill(min(100, score + 10), max(10, time_taken - 10), max(1, attempts - 1))
    scenarios.append({
        "change": "All metrics improve moderately",
        "icon": "🚀",
        "result_skill": best_skill,
        "result_conf": best_conf,
        "detail": f"If you score {min(100, score+10)}, finish in {max(10, time_taken-10)}min, and use {max(1, attempts-1)} attempt(s) → {best_skill} ({best_conf}%).",
    })

    return scenarios


# ─── Existing Utility Functions ─────────────────────────────────────────────────

def get_dataset_stats():
    global dataset_stats
    if dataset_stats is None:
        train_model()
    return dataset_stats

def get_resources(skill_level):
    resources = {
        "Beginner":     {"cpu": "1 vCPU",  "ram": "1 GB",  "gpu": "None",         "rate": 0.02},
        "Intermediate": {"cpu": "2 vCPU",  "ram": "4 GB",  "gpu": "Shared GPU",   "rate": 0.08},
        "Advanced":     {"cpu": "4 vCPU",  "ram": "8 GB",  "gpu": "Dedicated GPU", "rate": 0.20},
    }
    return resources.get(skill_level, resources["Beginner"])

def get_difficulty(skill_level):
    return {
        "Beginner":     "Easy",
        "Intermediate": "Medium",
        "Advanced":     "Hard"
    }.get(skill_level, "Easy")

def calculate_cost(skill_level, time_taken):
    r = get_resources(skill_level)
    hours = time_taken / 60.0
    return round(r["rate"] * hours, 4)


# Train on import
train_model()
