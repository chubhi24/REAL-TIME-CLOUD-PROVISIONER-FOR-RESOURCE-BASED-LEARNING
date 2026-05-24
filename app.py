from flask import Flask, render_template, request, redirect, url_for, session, jsonify, Response
from db import (init_db, create_user, get_user, save_result,
                get_all_results, get_user_results, get_leaderboard,
                get_all_users, get_stats, update_password, delete_user_cascade,
                save_learning_session, get_user_learning_sessions,
                save_billing_record, get_user_billing,
                create_tasks_for_goal, get_tasks_for_goal, start_task_session,
                mark_task_completed, get_task_session, get_task_completions,
                calculate_session_metrics, finalize_task_session)
from model import (predict_skill, get_resources, get_difficulty, calculate_cost,
                    explain_prediction, compare_with_dataset,
                    get_improvement_suggestions, what_if_analysis, get_dataset_stats)
from cloud_knowledge import (get_all_goals, get_learning_goal, get_resource_tier,
                              get_guidance, calculate_learning_cost, get_roadmap,
                              get_simulated_errors, get_cost_optimization,
                              generate_ai_coaching, get_tasks_for_goal as get_goal_tasks)
from billing_engine import (calculate_smart_billing, get_all_resources,
                             get_billing_summary_text, get_cost_simulation)
from insight_manager import (get_session_insights, get_performance_summary,
                             get_goal_progress, get_cost_insights,
                             get_comparison, get_recommendation, get_timeline)
import json
import csv
from io import StringIO

app = Flask(__name__)
app.secret_key = "cloudlearn_secret_2024"

init_db()

# Task library static data for dashboard
TASK_LIBRARY = [
    {
        "id": "compute-1",
        "category": "Compute",
        "name": "Launch EC2 Instance",
        "level": "Beginner",
        "description": "Launch an EC2 instance with basic security settings.",
        "required_resources": {
            "instance_type": "t2.micro",
            "hours": 2,
            "storage_gb": 20
        },
        "estimated_cost": 0.50
    },
    {
        "id": "compute-2",
        "category": "Compute",
        "name": "Auto-Scaling Group Setup",
        "level": "Intermediate",
        "description": "Configure ASG and load-based scaling rules.",
        "required_resources": {
            "instance_type": "t2.small",
            "hours": 4,
            "storage_gb": 30
        },
        "estimated_cost": 1.85
    },
    {
        "id": "storage-1",
        "category": "Storage",
        "name": "Create Versioned S3 Bucket",
        "level": "Beginner",
        "description": "Create an S3 bucket with versioning and security policies.",
        "required_resources": {
            "storage_gb": 50
        },
        "estimated_cost": 1.15
    },
    {
        "id": "monitoring-1",
        "category": "Monitoring",
        "name": "Setup CloudWatch Alarms",
        "level": "Intermediate",
        "description": "Monitor EC2 CPU and setup alerts for thresholds.",
        "required_resources": {
            "metrics": 1000,
            "retention_days": 30
        },
        "estimated_cost": 4.00
    },
    {
        "id": "devops-1",
        "category": "DevOps",
        "name": "CI/CD Pipeline with CodePipeline",
        "level": "Advanced",
        "description": "Create full CI/CD pipeline with CodePipeline and CodeBuild.",
        "required_resources": {
            "build_minutes": 60
        },
        "estimated_cost": 7.25
    },
    {
        "id": "ml-1",
        "category": "Machine Learning",
        "name": "Train ML Model on SageMaker",
        "level": "Advanced",
        "description": "Build and train a model with a managed SageMaker notebook.",
        "required_resources": {
            "model_size_gb": 10,
            "training_hours": 6,
            "compute_intensity": "high"
        },
        "estimated_cost": 156.00
    }
]
USER_TASK_PROGRESS = {}


def get_all_tasks():
    return TASK_LIBRARY


def get_task_by_id(task_id):
    for t in TASK_LIBRARY:
        if t["id"] == task_id:
            return t
    return None


def filter_task_library(category=None, level=None):
    filtered = TASK_LIBRARY
    if category:
        filtered = [t for t in filtered if t["category"] == category]
    if level:
        filtered = [t for t in filtered if t["level"] == level]
    return filtered


def get_user_task_progress(user_id):
    return USER_TASK_PROGRESS.get(user_id, {"started": set(), "completed": set(), "tasks": {}})


def update_user_task_progress(user_id, status, task_id):
    progress = USER_TASK_PROGRESS.setdefault(user_id, {"started": set(), "completed": set(), "tasks": {}})
    if status == "start":
        progress["started"].add(task_id)
        progress["tasks"].setdefault(task_id, {})["started_at"] = __import__("datetime").datetime.utcnow().isoformat()
    elif status == "complete":
        progress["completed"].add(task_id)
        progress["tasks"].setdefault(task_id, {})["completed_at"] = __import__("datetime").datetime.utcnow().isoformat()
    USER_TASK_PROGRESS[user_id] = progress
    return progress


def get_task_progress_summary(user_id):
    progress = get_user_task_progress(user_id)
    total = len(TASK_LIBRARY)
    completed = len(progress["completed"])
    category_progress = {}
    for task in TASK_LIBRARY:
        cat = task["category"]
        category_progress.setdefault(cat, {"total": 0, "completed": 0})
        category_progress[cat]["total"] += 1
        if task["id"] in progress["completed"]:
            category_progress[cat]["completed"] += 1
    return {
        "total_tasks": total,
        "completed_tasks": completed,
        "percent": int((completed/total)*100) if total>0 else 0,
        "category_progress": category_progress
    }


def recommend_next_task(user_id):
    progress = get_user_task_progress(user_id)
    completed = progress["completed"]
    available = [t for t in TASK_LIBRARY if t["id"] not in completed]
    if not available:
        return None

    # missing camera categories
    completed_cat = set(get_task_by_id(tid)["category"] for tid in completed if get_task_by_id(tid))
    missing = [c for c in {t["category"] for t in TASK_LIBRARY} if c not in completed_cat]
    if missing:
        for t in available:
            if t["category"] in missing:
                return t
    return available[0]

# ─── Auth ──────────────────────────────────────────────────────────────────────

@app.route("/")
def index():
    if "user_id" in session:
        return redirect(url_for("dashboard"))
    return redirect(url_for("login"))

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        user = get_user(username, password)
        if user:
            session["user_id"] = user["id"]
            session["username"] = user["username"]
            session["role"] = user["role"]
            if user["role"] == "admin":
                return redirect(url_for("admin"))
            return redirect(url_for("dashboard"))
        error = "Invalid username or password."
    return render_template("login.html", error=error)

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        username = request.form["username"].strip()
        password = request.form["password"].strip()
        if len(username) < 3:
            error = "Username must be at least 3 characters."
        elif len(password) < 4:
            error = "Password must be at least 4 characters."
        elif create_user(username, password):
            return redirect(url_for("login"))
        else:
            error = "Username already taken."
    return render_template("login.html", error=error, register=True)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

# ─── Dashboard ────────────────────────────────────────────────────────────────

@app.route("/dashboard")
def dashboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    history = get_user_results(session["user_id"])
    history = [dict(r) for r in history]

    # If no explicit results exist, fall back to recorded learning_sessions to populate charts
    if not history:
        session_rows = get_user_learning_sessions(session["user_id"])
        history = [
            {
                "score": 0,
                "time_taken": 0,
                "attempts": 0,
                "skill_level": row['skill_level'],
                "cost": row['cost'],
                "goal_key": row['goal_key'],
                "notes": row['goal_title'],
                "created_at": row['created_at']
            }
            for row in session_rows
        ]

    # Get global stats for comparison
    global_stats = get_stats()
    
    # Generate AI Insights
    latest_session = history[0] if history else None
    
    session_insight = get_session_insights(latest_session, history)
    perf_summary = get_performance_summary(history)
    goal_progress = get_goal_progress(history)
    cost_insight = get_cost_insights(latest_session, history)
    comparison = get_comparison(history, global_stats)
    recommendation = get_recommendation(latest_session)
    timeline = get_timeline(history)
    
    task_library = get_all_tasks()
    task_progress = get_task_progress_summary(session["user_id"])
    task_recommendation = recommend_next_task(session["user_id"])

    return render_template("dashboard.html",
                           username=session["username"],
                           history=history,
                           history_json=json.dumps(history),
                           session_insight=session_insight,
                           perf_summary=perf_summary,
                           goal_progress=goal_progress,
                           cost_insight=cost_insight,
                           comparison=comparison,
                           recommendation=recommendation,
                           timeline=timeline,
                           task_library=task_library,
                           task_progress=task_progress,
                           task_recommendation=task_recommendation)


@app.route("/api/tasklibrary")
def api_tasklibrary():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    category = request.args.get("category")
    level = request.args.get("level")
    tasks = filter_task_library(category=category, level=level)
    return jsonify({"tasks": tasks})


@app.route("/api/tasklibrary/start", methods=["POST"])
def api_tasklibrary_start():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    task_id = data.get("task_id")
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    update_user_task_progress(session["user_id"], "start", task_id)
    return jsonify({
        "success": True,
        "task": task,
        "estimated_cost": task.get("estimated_cost", 0.0),
        "progress": get_task_progress_summary(session["user_id"]) 
    })


@app.route("/api/tasklibrary/complete", methods=["POST"])
def api_tasklibrary_complete():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    data = request.get_json() or {}
    task_id = data.get("task_id")
    task = get_task_by_id(task_id)
    if not task:
        return jsonify({"error": "Task not found"}), 404

    update_user_task_progress(session["user_id"], "complete", task_id)
    return jsonify({
        "success": True,
        "task": task,
        "progress": get_task_progress_summary(session["user_id"]),
        "next_task": recommend_next_task(session["user_id"])
    })


@app.route("/api/tasklibrary/progress")
def api_tasklibrary_progress():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    return jsonify(get_task_progress_summary(session["user_id"]))


@app.route("/api/tasklibrary/recommendation")
def api_tasklibrary_recommendation():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    next_task = recommend_next_task(session["user_id"])
    return jsonify({"next_task": next_task})


@app.route("/api/performance_summary")
def api_performance_summary():
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    history = get_user_results(session["user_id"])
    history = [dict(r) for r in history]
    return jsonify(get_performance_summary(history))


@app.route("/predict", methods=["POST"])
def predict():
    if "user_id" not in session:
        return redirect(url_for("login"))

    score      = int(request.form["score"])
    time_taken = int(request.form["time_taken"])
    attempts   = int(request.form["attempts"])
    notes      = request.form.get("notes", "").strip()

    skill_level, confidence = predict_skill(score, time_taken, attempts)
    resources   = get_resources(skill_level)
    difficulty  = get_difficulty(skill_level)
    cost        = calculate_cost(skill_level, time_taken)

    # Generate intelligent insights
    explanation  = explain_prediction(score, time_taken, attempts, skill_level)
    comparison   = compare_with_dataset(score, time_taken, attempts)
    suggestions  = get_improvement_suggestions(score, time_taken, attempts, skill_level)
    whatif       = what_if_analysis(score, time_taken, attempts)
    ds_stats     = get_dataset_stats()

    save_result(
        session["user_id"], session["username"],
        score, time_taken, attempts, skill_level,
        difficulty, resources["cpu"], resources["ram"], resources["gpu"], cost, notes
    )

    return redirect(url_for("dashboard"))

# ─── Leaderboard ──────────────────────────────────────────────────────────────

@app.route("/leaderboard")
def leaderboard():
    if "user_id" not in session:
        return redirect(url_for("login"))
    board = get_leaderboard()
    board = [dict(r) for r in board]
    return render_template("leaderboard.html",
                           username=session["username"],
                           board=board)

# ─── Admin ─────────────────────────────────────────────────────────────────────

@app.route("/admin")
def admin():
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    stats   = get_stats()
    users   = get_all_users()
    results = get_all_results()
    users   = [dict(u) for u in users]
    results = [dict(r) for r in results]
    return render_template("admin.html",
                           username=session["username"],
                           stats=stats,
                           users=users,
                           results=results,
                           results_json=json.dumps(results))

@app.route("/admin/delete_user/<int:id>", methods=["POST"])
def admin_delete_user(id):
    if "user_id" not in session or session.get("role") != "admin":
        return redirect(url_for("login"))
    
    # Optional: prevent deleting oneself
    if session["user_id"] == id:
        pass # Handle admin self-deletion if needed
    else:
        delete_user_cascade(id)
    return redirect(url_for("admin"))

# ─── New Features ──────────────────────────────────────────────────────────────

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    error = None
    success = None
    if request.method == "POST":
        current_password = request.form["current_password"]
        new_password = request.form["new_password"]
        confirm_password = request.form["confirm_password"]
        
        user = get_user(session["username"], current_password)
        if not user:
            error = "Invalid current password."
        elif new_password != confirm_password:
            error = "New passwords do not match."
        elif len(new_password) < 4:
            error = "New password must be at least 4 characters."
        else:
            update_password(session["user_id"], new_password)
            success = "Password updated successfully."

    # Fetch stats for radar chart
    history = get_user_results(session["user_id"])
    history = [dict(r) for r in history]
    
    total_sessions = len(history)
    avg_score = sum(r["score"] for r in history) / total_sessions if total_sessions else 0
    best_score = max(r["score"] for r in history) if total_sessions else 0
    avg_cost = sum(r["cost"] for r in history) / total_sessions if total_sessions else 0
    skill_dist = {"Beginner": 0, "Intermediate": 0, "Advanced": 0}
    for r in history:
        skill_dist[r["skill_level"]] = skill_dist.get(r["skill_level"], 0) + 1
        
    stats = {
        "total_sessions": total_sessions,
        "avg_score": round(avg_score, 1),
        "best_score": best_score,
        "avg_cost": round(avg_cost, 2),
        "skill_dist": skill_dist
    }
    
    return render_template("profile.html", 
                           username=session["username"], 
                           stats=stats, 
                           history_json=json.dumps(history),
                           error=error, 
                           success=success)

@app.route("/api/stats")
def api_stats():
    stats = get_stats()
    return jsonify({
        "total_users": stats["total_users"],
        "total_sessions": stats["total_sessions"],
        "average_score": stats["avg_score"],
        "skill_distribution": {
            "beginner": stats["skill_dist"].get("Beginner", 0),
            "intermediate": stats["skill_dist"].get("Intermediate", 0),
            "advanced": stats["skill_dist"].get("Advanced", 0)
        }
    })

@app.route("/export")
def export_history():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    history = get_user_results(session["user_id"])
    
    si = StringIO()
    cw = csv.writer(si)
    cw.writerow(["score", "time", "attempts", "skill", "cost", "notes", "timestamp"])
    for r in history:
        cw.writerow([
            r["score"], 
            r["time_taken"], 
            r["attempts"], 
            r["skill_level"], 
            r["cost"], 
            r["notes"], 
            r["created_at"]
        ])
    
    output = si.getvalue()
    return Response(
        output,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename=history_{session['username']}.csv"}
    )

# ─── Cloud Learning Path Recommender ──────────────────────────────────────────

@app.route("/learn")
def learn():
    if "user_id" not in session:
        return redirect(url_for("login"))
    goals = get_all_goals()
    # Get user's past learning sessions
    past_sessions = get_user_learning_sessions(session["user_id"])
    past_sessions = [dict(s) for s in past_sessions]
    return render_template("learn.html",
                           username=session["username"],
                           goals=goals,
                           past_sessions=past_sessions)

@app.route("/api/cost_simulation/<goal_key>")
def api_cost_simulation(goal_key):
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
        
    history = get_user_results(session["user_id"])
    history = [dict(r) for r in history]
    
    if history:
        avg_score = sum(r["score"] for r in history) / len(history)
        avg_time = sum(r["time_taken"] for r in history) / len(history)
        avg_attempts = sum(r["attempts"] for r in history) / len(history)
        skill_level, _ = predict_skill(
            int(avg_score), int(avg_time), int(avg_attempts)
        )
    else:
        goal = get_learning_goal(goal_key)
        skill_level = goal["base_difficulty"] if goal else "Beginner"
        
    simulation = get_cost_simulation(goal_key, skill_level)
    return jsonify(simulation)

@app.route("/learn/start", methods=["GET", "POST"])
def learn_start():
    if "user_id" not in session:
        return redirect(url_for("login"))

    if request.method == 'GET':
        goal_key = request.args.get("goal", "").strip()
        highlighted_task_id = request.args.get("task_id", "").strip()
    else:
        goal_key = request.form.get("goal", "").strip()
        highlighted_task_id = request.form.get("task_id", "").strip()

    goal = get_learning_goal(goal_key)
    if not goal:
        return redirect(url_for("learn"))

    highlight_task_name = None
    if highlighted_task_id:
        highlight_task = get_task_by_id(highlighted_task_id)
        if highlight_task:
            highlight_task_name = highlight_task["name"]

    # Use existing user history to determine skill level via ML
    history = get_user_results(session["user_id"])
    history = [dict(r) for r in history]

    if history:
        avg_score = sum(r["score"] for r in history) / len(history)
        avg_time = sum(r["time_taken"] for r in history) / len(history)
        avg_attempts = sum(r["attempts"] for r in history) / len(history)
        skill_level, confidence = predict_skill(
            int(avg_score), int(avg_time), int(avg_attempts)
        )
    else:
        avg_score, avg_time, avg_attempts = 50.0, 30.0, 3.0
        skill_level = goal["base_difficulty"]
        confidence = 100.0

    # 0. Check for manual override tier
    override_tier = request.form.get("override_tier")
    if override_tier in ["Beginner", "Intermediate", "Advanced"]:
        skill_level = override_tier
        confidence = 100.0  # Manual selection
    
    # 1. Resource tier
    tier = get_resource_tier(skill_level)
    cost = calculate_learning_cost(skill_level, goal["estimated_time"])
    guidance = get_guidance(goal_key, skill_level)

    # 2. Learning Roadmap
    roadmap = get_roadmap(goal_key)

    # 3. Error Simulation
    errors = get_simulated_errors(goal_key, count=2)

    # 4. Cost Optimization
    cost_opt = get_cost_optimization(skill_level)

    # 5. AI Coach
    coaching = generate_ai_coaching(avg_score, avg_time, avg_attempts, skill_level, goal_key)

    # 6. Save old learning session for backward compatibility
    save_learning_session(
        session["user_id"], session["username"],
        goal_key, goal["title"], skill_level,
        tier["instance_type"], tier["cpu"], tier["ram"], tier["gpu"], cost
    )
    
    # 7. Create task-based learning session
    task_session_id = start_task_session(session["user_id"], goal_key, goal["title"])
    
    # 8. Initialize tasks for this goal if not already done
    tasks = get_goal_tasks(goal_key)
    if tasks:
        create_tasks_for_goal(goal_key, tasks)

    # Build result for template
    learn_result = {
        "goal": goal,
        "goal_key": goal_key,
        "skill_level": skill_level,
        "confidence": confidence,
        "tier": tier,
        "cost": cost,
        "guidance": guidance,
        "roadmap": roadmap,
        "errors": errors,
        "cost_opt": cost_opt,
        "coaching": coaching,
        "task_session_id": task_session_id,
        "tasks": tasks,
        "highlighted_task_id": highlighted_task_id,
        "highlight_task_name": highlight_task_name
    }

    goals = get_all_goals()
    past_sessions = get_user_learning_sessions(session["user_id"])
    past_sessions = [dict(s) for s in past_sessions]
    task_library = get_all_tasks()
    return render_template("learn.html",
                           username=session["username"],
                           goals=goals,
                           learn_result=learn_result,
                           task_library=task_library,
                           past_sessions=past_sessions)

# ─── Task Management APIs ──────────────────────────────────────────────────────

@app.route("/api/session/tasks/<int:session_id>")
def api_session_tasks(session_id):
    """Get tasks for a learning session."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    task_session = get_task_session(session_id)
    if not task_session or task_session["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    
    # Get all tasks for this goal
    tasks = get_goal_tasks(task_session["goal_key"])
    
    # Get completed tasks
    completions = get_task_completions(session_id)
    completed_task_names = {dict(c)["task_name"] for c in completions}
    
    # Build task list with completion status
    task_list = []
    for idx, task in enumerate(tasks, 1):
        task_list.append({
            "id": idx,
            "name": task,
            "completed": task in completed_task_names
        })
    
    return jsonify({
        "session_id": session_id,
        "goal_key": task_session["goal_key"],
        "goal_title": task_session["goal_title"],
        "tasks": task_list,
        "tasks_completed": task_session["tasks_completed"],
        "tasks_total": task_session["tasks_total"]
    })

@app.route("/api/task/complete", methods=["POST"])
def api_task_complete():
    """Mark a task as completed."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    session_id = data.get("session_id")
    task_name = data.get("task_name")
    attempts = data.get("attempts", 1)
    
    if not session_id or not task_name:
        return jsonify({"error": "Missing session_id or task_name"}), 400
    
    task_session = get_task_session(session_id)
    if not task_session or task_session["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    
    # Find task ID
    tasks = get_goal_tasks(task_session["goal_key"])
    task_id = None
    for idx, task in enumerate(tasks, 1):
        if task == task_name:
            task_id = idx
            break
    
    if task_id is None:
        return jsonify({"error": "Task not found"}), 404
    
    # Mark task as completed in both session DB and task library progress tracker
    mark_task_completed(session_id, session["user_id"], task_id, task_name, attempts)
    update_user_task_progress(session["user_id"], "complete", task_id)
    
    # Get updated progress and next category-level summary
    metrics = calculate_session_metrics(session_id)
    updated_session = dict(get_task_session(session_id))
    task_progress = get_task_progress_summary(session["user_id"])
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "tasks_completed": updated_session["tasks_completed"],
        "tasks_total": updated_session["tasks_total"],
        "progress_pct": int((updated_session["tasks_completed"] / updated_session["tasks_total"]) * 100) if updated_session["tasks_total"] > 0 else 0,
        "category_progress": task_progress["category_progress"]
    })

@app.route("/api/session/progress/<int:session_id>")
def api_session_progress(session_id):
    """Get progress for a learning session."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    task_session = get_task_session(session_id)
    if not task_session or task_session["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    
    metrics = calculate_session_metrics(session_id)
    
    return jsonify({
        "session_id": session_id,
        "tasks_completed": task_session["tasks_completed"],
        "tasks_total": task_session["tasks_total"],
        "progress_pct": int((task_session["tasks_completed"] / task_session["tasks_total"]) * 100) if task_session["tasks_total"] > 0 else 0,
        "metrics": {
            "score": metrics["score"],
            "attempts": metrics["attempts"]
        }
    })

@app.route("/api/session/finalize", methods=["POST"])
def api_session_finalize():
    """Finalize a task session and calculate skill level."""
    if "user_id" not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    data = request.get_json()
    session_id = data.get("session_id")
    
    if not session_id:
        return jsonify({"error": "Missing session_id"}), 400
    
    task_session = get_task_session(session_id)
    if not task_session or task_session["user_id"] != session["user_id"]:
        return jsonify({"error": "Not found"}), 404
    
    # Calculate metrics
    metrics = calculate_session_metrics(session_id)
    
    # Predict skill level based on calculated metrics plus time
    history = get_user_results(session["user_id"])
    if history:
        avg_time = sum(dict(r)["time_taken"] for r in history) / len(history)
    else:
        avg_time = 30
    
    skill_level, confidence = predict_skill(metrics["score"], int(avg_time), metrics["attempts"])
    
    # Finalize session
    finalize_task_session(session_id, skill_level)
    
    # Update the results entry (if it exists from older system)
    updated_session = dict(get_task_session(session_id))
    
    return jsonify({
        "success": True,
        "session_id": session_id,
        "skill_level": skill_level,
        "confidence": round(confidence, 1),
        "score": metrics["score"],
        "attempts": metrics["attempts"]
    })

# ─── Smart Billing Engine ─────────────────────────────────────────────────────

def attempt_multiplier(attempts):
    attempts = int(attempts or 1)
    if attempts == 1:
        return 1.0
    if 2 <= attempts <= 3:
        return 1.2
    if 4 <= attempts <= 5:
        return 1.5
    return 2.0


def classify_cost_level(cost):
    if cost <= 20:
        return "Low"
    if cost <= 75:
        return "Moderate"
    return "High"


def calculate_service_base_cost(service, data):
    service = service.lower()
    breakdown = []
    optimization = []
    base_cost = 0.0

    if service == "ec2":
        instance_type = data.get("instance_type", "t2.micro")
        hours = float(data.get("hours", 0) or 0)
        storage_gb = float(data.get("storage_gb", 0) or 0)

        instance_rates = {
            "t2.micro": 0.011,
            "t2.small": 0.023,
            "t2.medium": 0.046,
            "t3.large": 0.083,
            "m5.large": 0.096
        }
        storage_rate = 0.025

        instance_cost = instance_rates.get(instance_type, 0.011) * hours
        storage_cost = storage_rate * storage_gb
        breakdown.append({"name": "EC2 Instance", "value": round(instance_cost, 2)})
        breakdown.append({"name": "EC2 Storage", "value": round(storage_cost, 2)})
        base_cost = round(instance_cost + storage_cost, 2)

        if instance_type in ["t2.medium", "m5.large"] and hours > 24:
            optimization.append("Use reserved instances for sustained workloads to cut compute cost by up to 40%.")
        if storage_gb > 500:
            optimization.append("Move cold data to S3 Glacier to reduce storage cost on large volumes.")

    elif service == "s3":
        storage_gb = float(data.get("storage_gb", 0) or 0)
        requests = float(data.get("requests", 0) or 0)

        storage_cost = 0.023 * storage_gb
        request_cost = 0.0004 * requests
        breakdown.append({"name": "S3 Storage", "value": round(storage_cost, 2)})
        breakdown.append({"name": "S3 Requests", "value": round(request_cost, 2)})
        base_cost = round(storage_cost + request_cost, 2)

        if storage_gb > 1000:
            optimization.append("Enable Intelligent-Tiering for >1TB to lower infrequent access charges.")

    elif service in ["machine_learning", "ml"]:
        model_size_gb = float(data.get("model_size_gb", 0) or 0)
        training_hours = float(data.get("training_hours", 0) or 0)
        intensity = data.get("compute_intensity", "medium").lower()

        intensity_rates = {"low": 5.0, "medium": 12.0, "high": 25.0}
        storage_rate = 0.12

        compute_cost = intensity_rates.get(intensity, 12.0) * training_hours
        model_cost = model_size_gb * storage_rate
        breakdown.append({"name": "ML Training", "value": round(compute_cost, 2)})
        breakdown.append({"name": "Model Storage", "value": round(model_cost, 2)})
        base_cost = round(compute_cost + model_cost, 2)

        if intensity == "high" and training_hours > 8:
            optimization.append("Lower intensity or schedule spot instances to reduce ML training cost by 50%.")

    elif service == "cloud_monitoring":
        metrics = float(data.get("metrics", 1000) or 0)
        retention_days = float(data.get("retention_days", 30) or 0)

        metric_cost = 0.0002 * metrics
        retention_cost = 0.005 * retention_days
        breakdown.append({"name": "Monitoring Ingestion", "value": round(metric_cost, 2)})
        breakdown.append({"name": "Retention", "value": round(retention_cost, 2)})
        base_cost = round(metric_cost + retention_cost, 2)

        if retention_days > 30:
            optimization.append("Use retention policies to archive older metrics and reduce costs.")

    elif service == "loadbalancer":
        hours = float(data.get("hours", 0) or 0)
        processed_gb = float(data.get("processed_gb", 0) or 0)

        lb_cost = 0.08 * hours
        data_cost = 0.01 * processed_gb
        breakdown.append({"name": "Load Balancer", "value": round(lb_cost, 2)})
        breakdown.append({"name": "Data Processed", "value": round(data_cost, 2)})
        base_cost = round(lb_cost + data_cost, 2)

        if processed_gb > 1000:
            optimization.append("Enable compression/caching to dramatically reduce LB data processing costs.")

    else:
        breakdown.append({"name": "Unknown Service", "value": 0.0})

    return base_cost, breakdown, optimization


def generate_cost_graph(services, data):
    if isinstance(services, str):
        services = [services]

    graph = []
    for attempts in range(1, 7):
        total = 0.0
        for svc in services:
            base_cost, _, _ = calculate_service_base_cost(svc, data)
            total += base_cost * attempt_multiplier(attempts)
        graph.append({"attempt": attempts, "cost": round(total, 2)})
    return graph


def calculate_resource_cost(service, data, attempts=1):
    base_cost, breakdown, optimization = calculate_service_base_cost(service, data)
    multiplier = attempt_multiplier(attempts)
    final_cost = round(base_cost * multiplier, 2)
    savings = round(final_cost - base_cost, 2)

    if attempts == 1:
        optimization.append("Single attempt success gives you the best cost profile (1.0x multiplier).")
    else:
        optimization.append(f"Attempt multiplier {multiplier}x applied based on {attempts} attempts.")

    return {
        "service": service,
        "service_name": service.replace('_', ' ').title(),
        "base_cost": base_cost,
        "final_cost": final_cost,
        "multiplier": multiplier,
        "savings": savings,
        "savings_pct": round((savings / base_cost * 100), 1) if base_cost > 0 else 0,
        "cost_warning": classify_cost_level(final_cost),
        "breakdown": breakdown,
        "optimization": optimization,
        "rewards": [{
            "title": "Attempt-based Incentive",
            "detail": "1.0x multiplier for first attempt; higher multipliers apply for repeat attempts.",
            "value": (0.2 if attempts == 1 else 0.0)
        }],
        "cost_graph": generate_cost_graph(service, data)
    }


@app.route("/billing")
def billing():
    if "user_id" not in session:
        return redirect(url_for("login"))
    goals = get_all_goals()
    resources = get_all_resources()
    past_bills = get_user_billing(session["user_id"])
    past_bills = [dict(b) for b in past_bills]
    return render_template("billing.html",
                           username=session["username"],
                           goals=goals,
                           resources=resources,
                           past_bills=past_bills)

@app.route("/billing/calculate", methods=["POST"])
def billing_calculate():
    if "user_id" not in session:
        return redirect(url_for("login"))

    service = request.form.get("service", "").strip().lower()
    if not service:
        return redirect(url_for("billing"))

    attempts = int(request.form.get("attempts", 1) or 1)

    if service == "all_services":
        selected = request.form.getlist("selected_services")
        if not selected:
            selected = ["ec2", "s3", "machine_learning", "cloud_monitoring", "loadbalancer"]

        combined_base = 0.0
        combined_final = 0.0
        combined_breakdown = []
        combined_optimization = []
        resources_used = []

        for svc in selected:
            item = calculate_resource_cost(svc, request.form, attempts)
            combined_base += item["base_cost"]
            combined_final += item["final_cost"]
            combined_breakdown.append({"name": item["service_name"], "value": item["final_cost"]})
            combined_optimization.extend(item.get("optimization", []))
            resources_used.append({"name": item["service_name"], "session_cost": f"{item['final_cost']:.2f}"})

        savings = round(combined_final - combined_base, 2)
        billing_data = {
            "service_name": "All Selected Resources",
            "base_cost": round(combined_base, 2),
            "final_cost": round(combined_final, 2),
            "savings": savings,
            "savings_pct": round(abs(savings) / max(combined_base, 1) * 100, 1),
            "cost_warning": classify_cost_level(combined_final),
            "breakdown": combined_breakdown,
            "optimization": combined_optimization,
            "resources_used": resources_used,
            "cost_graph": generate_cost_graph(selected, request.form),
            "rewards": [{"title": "Attempt-based Incentive", "detail": "First attempt is cheapest; repeated attempts increase multiplier.", "value": (0.2 if attempts == 1 else 0.0)}]
        }

    else:
        billing_data = calculate_resource_cost(service, request.form, attempts)
        billing_data["service_name"] = service.replace("_", " ").title()
        billing_data["resources_used"] = [{"name": billing_data["service_name"], "session_cost": f"{billing_data['final_cost']:.2f}"}]
        billing_data["cost_graph"] = generate_cost_graph(service, request.form)

        if attempts == 1:
            billing_data["rewards"] = [{"title": "First Attempt Economy", "detail": "1.0x multiplier with best cost for one try.", "value": 0.2}]
        else:
            billing_data["rewards"] = [{"title": "Repeat Attempt Adjustment", "detail": f"{attempts} attempts applied at {attempt_multiplier(attempts)}x multiplier.", "value": 0.0}]

    res_summary = ", ".join([f"{item['name']}(${item['value']:.2f})" for item in billing_data.get("breakdown", [])])
    save_billing_record(
        session["user_id"], session["username"],
        service, billing_data["service_name"],
        billing_data["final_cost"],
        "Smart", attempts,
        billing_data["base_cost"],
        billing_data["savings_pct"], billing_data["rewards"][0]["value"],
        res_summary
    )

    goals = get_all_goals()
    resources = get_all_resources()
    past_bills = get_user_billing(session["user_id"])
    past_bills = [dict(b) for b in past_bills]
    return render_template("billing.html",
                           username=session["username"],
                           goals=goals,
                           resources=resources,
                           billing_result=billing_data,
                           selected_goal={"title": billing_data["service_name"]},
                           past_bills=past_bills)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002, debug=True)
