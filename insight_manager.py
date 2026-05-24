# ═══════════════════════════════════════════════════════════════════════════════
# AI Learning Insight & Recommendation Engine
# ═══════════════════════════════════════════════════════════════════════════════
import json
from cloud_knowledge import LEARNING_GOALS, ROADMAPS

# ─── 1. Session Insight Engine ──────────────────────────────────────────────────

def get_session_insights(latest, history):
    """Generate intelligent feedback for the most recent session."""
    if not latest:
        return None

    score = latest.get('score', 0)
    time = latest.get('time_taken', 30)
    attempts = latest.get('attempts', 1)
    notes = latest.get('notes', '')
    skill = latest.get('skill_level', 'Beginner')

    # Find topic from notes
    topic_key = _find_topic_key(notes)
    topic_name = LEARNING_GOALS.get(topic_key, {}).get('title', 'this task')

    insights = {
        "summary": f"In your latest session on **{topic_name}**, you achieved a **{skill}** level.",
        "strength": None,
        "weakness": None,
        "action": None
    }

    # Strength logic
    if score >= 90:
        insights["strength"] = "High precision — your theoretical knowledge is excellent."
    elif time < 20:
        insights["strength"] = "Fast execution — you handle terminal operations very efficiently."
    elif attempts == 1:
        insights["strength"] = "First-time success — great focus and preparation."
    else:
        insights["strength"] = "Persistence — you're staying committed to the learning path."

    # Weakness logic
    if attempts > 3:
        insights["weakness"] = "High retry count — you're relying on trial-and-error."
    elif score < 60:
        insights["weakness"] = "Concept gap — the core logic of this service isn't fully clear yet."
    elif time > 50:
        insights["weakness"] = "Slow throughput — possibly blocked by configuration complexity."
    else:
        insights["weakness"] = "Marginal optimization — some resources were slightly over-provisioned."

    # Improvement action
    if skill == "Beginner":
        insights["action"] = "Focus on the foundational architecture before moving to advanced configurations."
    elif skill == "Intermediate":
        insights["action"] = "Try automating the setup using scripts or templates next time."
    else:
        insights["action"] = "Focus on cost-optimization and high-availability patterns."

    return insights

# ─── 2. Performance Summary ─────────────────────────────────────────────────────

def get_performance_summary(history):
    """Aggregate history into key performance cards."""
    if not history:
        return {
            "best_skill": "N/A", "avg_time": 0, "avg_attempts": 0, "total_cost": 0.0, "total_sessions": 0
        }

    skills = [h['skill_level'] for h in history]
    # Priority: Advanced > Intermediate > Beginner
    best_skill = "Beginner"
    if "Advanced" in skills: best_skill = "Advanced"
    elif "Intermediate" in skills: best_skill = "Intermediate"

    avg_time = sum(h['time_taken'] for h in history) / len(history)
    avg_attempts = sum(h['attempts'] for h in history) / len(history)
    total_cost = sum(h['cost'] for h in history)

    avg_savings_pct = round(sum(h.get('savings_pct', 0) for h in history) / len(history), 1)
    return {
        "best_skill": best_skill,
        "avg_time": round(avg_time, 1),
        "avg_attempts": round(avg_attempts, 1),
        "avg_savings_pct": avg_savings_pct,
        "total_cost": round(total_cost, 4),
        "total_sessions": len(history)
    }

# ─── 3. Goal Progress Tracker ───────────────────────────────────────────────────

def get_goal_progress(history):
    """Track progress per topic based on session history."""
    progress = {}
    
    for key, goal in LEARNING_GOALS.items():
        # Count sessions for this topic
        topic_sessions = [h for h in history if key in h.get('notes', '').lower() or key in h.get('goal_key', '').lower()]
        count = len(topic_sessions)
        
        # Mastery if highest score > 85
        max_score = max([s['score'] for s in topic_sessions]) if topic_sessions else 0
        
        # Progress calculation logic (simple)
        # 0 sessions = 0%, 1 session = 40%, 2 sessions = 70%, 3+ sessions or score > 85 = 100%
        prog_pct = 0
        if count == 1: prog_pct = 40
        elif count == 2: prog_pct = 70
        elif count >= 3 or max_score >= 85: prog_pct = 100
        
        progress[key] = {
            "title": goal["title"],
            "icon": goal["icon"],
            "pct": prog_pct,
            "sessions": count,
            "mastery": max_score >= 85
        }
        
    return progress

# ─── 4. Cost Insight System ─────────────────────────────────────────────────────

def get_cost_insights(latest, history):
    """Provide feedback on cost efficiency."""
    if not latest: return None
    
    cost = latest.get('cost', 0)
    avg_cost = sum(h['cost'] for h in history) / len(history) if history else cost
    
    insight = {
        "cost": round(cost, 4),
        "diff": round(cost - avg_cost, 4),
        "is_higher": cost > avg_cost,
        "tip": "Cost is optimal for your current tier."
    }
    
    if cost > 0.1:
        insight["tip"] = "Try using cheaper instance types (t2.micro) or spot instances."
    elif latest.get('skill_level') == 'Advanced' and cost < 0.05:
        insight["tip"] = "Excellent cost optimization for an advanced workload!"
    elif latest.get('attempts', 0) > 3:
        insight["tip"] = "Multiple attempts are increasing your cumulative session cost. Review documentation before retrying."
        
    return insight

# ─── 5. Smart Comparison Engine ──────────────────────────────────────────────────

def get_comparison(history, global_stats):
    """Compare user performance with global averages."""
    if not history or not global_stats: return None
    
    user_avg_score = sum(h['score'] for h in history) / len(history)
    user_avg_time = sum(h['time_taken'] for h in history) / len(history)
    
    global_avg_score = global_stats.get('avg_score', 65)
    global_avg_sessions = global_stats.get('total_sessions', 100) / max(1, global_stats.get('total_users', 10))
    
    return {
        "score_diff": round(user_avg_score - global_avg_score, 1),
        "is_better_score": user_avg_score > global_avg_score,
        "speed_diff": round(user_avg_time - 35, 1), # Assuming 35 is global avg time
        "is_faster": user_avg_time < 35,
        "status": "Top Learner" if user_avg_score > global_avg_score + 15 else "Active Learner"
    }

# ─── 6. Next Step Recommendation ────────────────────────────────────────────────

TOPIC_SEQUENCE = ["ec2", "s3", "cloudwatch", "loadbalancer", "webapp", "serverless"]

def get_recommendation(latest):
    """Suggest what to learn next."""
    if not latest:
        return {"topic": "EC2 Essentials", "reason": "Perfect starting point for cloud compute.", "icon": "🖥️"}
    
    notes = latest.get('notes', '').lower()
    skill = latest.get('skill_level', 'Beginner')
    score = latest.get('score', 0)
    
    if score < 60:
        # Suggest revision
        topic_key = _find_topic_key(notes)
        goal = LEARNING_GOALS.get(topic_key, {"title": "Previous Topic", "icon": "🔄"})
        return {
            "topic": f"Revision: {goal['title']}",
            "reason": "Mastering the fundamentals before moving on will build a stronger foundation.",
            "icon": "📚"
        }
    
    # Sequence logic
    current_topic = _find_topic_key(notes)
    try:
        idx = TOPIC_SEQUENCE.index(current_topic)
        if idx < len(TOPIC_SEQUENCE) - 1:
            next_topic_key = TOPIC_SEQUENCE[idx + 1]
            goal = LEARNING_GOALS.get(next_topic_key)
            return {
                "topic": goal["title"],
                "reason": f"Based on your {skill} skill, this is the logical next step.",
                "icon": goal["icon"]
            }
    except:
        pass
        
    return {
        "topic": "Serverless Architecture",
        "reason": "Challenge yourself with event-driven design patterns.",
        "icon": "⚡"
    }

# ─── 7. Smart Learning Timeline ─────────────────────────────────────────────────

def get_timeline(history):
    """Generate timeline data with improvement markers."""
    timeline = []
    
    # Process from oldest to newest to calculate improvement
    sorted_hist = sorted(history, key=lambda x: x['created_at'])
    
    prev_score = None
    for i, session in enumerate(reversed(sorted_hist)): # Reverse for UI (latest first)
        improvement = 0
        if i < len(sorted_hist) - 1:
            # We need the previous one in chronological order
            # Since we reversed sorted_hist above for display, 
            # let's be careful.
            pass
            
    # Simpler: just iterate and calculate improvement vs previous chrono session
    chrono_hist = sorted_hist
    for i in range(len(chrono_hist)):
        session = chrono_hist[i]
        improvement = 0
        if i > 0:
            improvement = session['score'] - chrono_hist[i-1]['score']
            
        timeline.append({
            "date": session['created_at'][:10],
            "topic": session.get('notes', 'Resource Training'),
            "skill": session['skill_level'],
            "score": session['score'],
            "time": session['time_taken'],
            "attempts": session['attempts'],
            "improvement": improvement
        })
        
    return list(reversed(timeline)) # Return latest first

# ─── Helper Functions ──────────────────────────────────────────────────────────

def _find_topic_key(text):
    text = text.lower()
    for key in LEARNING_GOALS.keys():
        if key in text:
            return key
    return "ec2" # Default
