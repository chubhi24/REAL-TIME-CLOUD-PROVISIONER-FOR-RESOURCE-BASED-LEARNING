# ═══════════════════════════════════════════════════════════════════════════════
# Hybrid Smart Cloud Billing Engine
# Resource-Based + Learning Efficiency Cost System
# ═══════════════════════════════════════════════════════════════════════════════

# ─── 1. Resource Cost Catalog ───────────────────────────────────────────────────

RESOURCE_CATALOG = {
    "ec2": {
        "name": "EC2 Compute",
        "icon": "🖥️",
        "base_cost_hr": 0.12,
        "category": "Compute",
        "description": "Virtual server instances for general compute workloads.",
    },
    "s3": {
        "name": "S3 Storage",
        "icon": "🪣",
        "base_cost_hr": 0.03,
        "category": "Storage",
        "description": "Object storage for files, backups, and static assets.",
    },
    "cloudwatch": {
        "name": "CloudWatch Monitoring",
        "icon": "📊",
        "base_cost_hr": 0.05,
        "category": "Monitoring",
        "description": "Metrics, alarms, dashboards, and log analytics.",
    },
    "loadbalancer": {
        "name": "Load Balancer (ALB)",
        "icon": "⚖️",
        "base_cost_hr": 0.08,
        "category": "Networking",
        "description": "Application load balancing across multiple targets.",
    },
    "ml_training": {
        "name": "ML Model Training",
        "icon": "🤖",
        "base_cost_hr": 0.45,
        "category": "AI/ML",
        "description": "SageMaker-style training for machine learning models.",
    },
    "gpu_compute": {
        "name": "GPU Compute (p3.2xlarge)",
        "icon": "🎮",
        "base_cost_hr": 1.20,
        "category": "High Performance",
        "description": "GPU-accelerated instances for deep learning and HPC.",
    },
    "rds": {
        "name": "RDS Database",
        "icon": "🗄️",
        "base_cost_hr": 0.10,
        "category": "Database",
        "description": "Managed relational database (MySQL/PostgreSQL).",
    },
    "lambda": {
        "name": "Lambda (Serverless)",
        "icon": "⚡",
        "base_cost_hr": 0.02,
        "category": "Serverless",
        "description": "Event-driven, pay-per-invocation compute.",
    },
}

# Map learning goals to primary resources used
GOAL_RESOURCES = {
    "ec2":           ["ec2", "cloudwatch"],
    "s3":            ["s3", "cloudwatch"],
    "cloudwatch":    ["cloudwatch", "ec2"],
    "webapp":        ["ec2", "rds", "loadbalancer", "s3", "cloudwatch"],
    "loadbalancer":  ["loadbalancer", "ec2", "cloudwatch"],
    "serverless":    ["lambda", "s3", "cloudwatch"],
}


# ─── 2. Efficiency Calculator ───────────────────────────────────────────────────

def calculate_efficiency(score, time_taken, attempts):
    """
    Calculate learning efficiency from performance metrics.
    Returns dict with level, factor, score breakdown, and explanation.
    """
    # Normalize each factor to 0-100
    score_norm = min(100, max(0, score))
    time_norm = min(100, max(0, 100 - (time_taken - 10) * 1.2))  # Lower time = higher efficiency
    attempt_norm = min(100, max(0, 100 - (attempts - 1) * 20))   # Fewer attempts = higher

    # Weighted composite
    efficiency_score = round(score_norm * 0.45 + time_norm * 0.25 + attempt_norm * 0.30, 1)

    if efficiency_score >= 75:
        level = "High"
        factor = 1.0
        explanation = "Excellent performance! You used resources optimally with strong results."
    elif efficiency_score >= 45:
        level = "Medium"
        factor = 0.6
        explanation = "Decent performance. Some resources were underutilized — room for optimization."
    else:
        level = "Low"
        factor = 0.3
        explanation = "Resources were heavily used relative to output. Guided learning recommended."

    return {
        "efficiency_score": efficiency_score,
        "level": level,
        "factor": factor,
        "explanation": explanation,
        "breakdown": {
            "score_component": round(score_norm * 0.45, 1),
            "time_component": round(time_norm * 0.25, 1),
            "attempt_component": round(attempt_norm * 0.30, 1),
        },
    }


# ─── 3. Smart Billing Calculator ───────────────────────────────────────────────

def calculate_smart_billing(goal_key, score, time_taken, attempts, session_duration_min=None):
    """
    Full billing calculation combining resource cost + efficiency.
    Returns comprehensive billing report.
    """
    if session_duration_min is None:
        session_duration_min = time_taken

    # Get resources for this goal
    resource_keys = GOAL_RESOURCES.get(goal_key, ["ec2"])
    resources_used = []
    total_base_cost = 0.0

    for rk in resource_keys:
        res = RESOURCE_CATALOG.get(rk, RESOURCE_CATALOG["ec2"])
        hours = session_duration_min / 60.0
        cost = round(res["base_cost_hr"] * hours, 4)
        total_base_cost += cost
        resources_used.append({
            "key": rk,
            "name": res["name"],
            "icon": res["icon"],
            "category": res["category"],
            "base_cost_hr": res["base_cost_hr"],
            "session_cost": round(cost, 4),
        })

    total_base_cost = round(total_base_cost, 4)

    # Calculate efficiency
    efficiency = calculate_efficiency(score, time_taken, attempts)

    # Apply efficiency factor
    final_cost = round(total_base_cost * efficiency["factor"], 4)
    savings = round(total_base_cost - final_cost, 4)
    savings_pct = round((1 - efficiency["factor"]) * 100, 0) if total_base_cost > 0 else 0

    # Rewards
    rewards = _calculate_rewards(efficiency, final_cost)

    # Misuse detection
    misuse = _detect_misuse(score, time_taken, attempts, efficiency)

    return {
        "resources_used": resources_used,
        "total_base_cost": total_base_cost,
        "efficiency": efficiency,
        "final_cost": final_cost,
        "savings": savings,
        "savings_pct": int(savings_pct),
        "rewards": rewards,
        "misuse": misuse,
        "session_duration_min": session_duration_min,
    }


# ─── 4. Reward System ──────────────────────────────────────────────────────────

def _calculate_rewards(efficiency, final_cost):
    """Generate rewards based on efficiency level."""
    rewards = []

    if efficiency["level"] == "High":
        credit = round(final_cost * 0.15, 4)
        rewards.append({
            "icon": "🏆", "type": "bonus_credit",
            "title": "Efficiency Bonus",
            "detail": f"15% bonus credit (${credit}) for high-efficiency usage.",
            "value": credit,
        })
        rewards.append({
            "icon": "⭐", "type": "badge",
            "title": "Cloud Optimizer Badge",
            "detail": "You've earned the Cloud Optimizer badge for efficient resource usage!",
            "value": 0,
        })
    elif efficiency["level"] == "Medium":
        credit = round(final_cost * 0.05, 4)
        rewards.append({
            "icon": "💡", "type": "bonus_credit",
            "title": "Learning Discount",
            "detail": f"5% learning credit (${credit}) — keep improving!",
            "value": credit,
        })
    else:
        rewards.append({
            "icon": "🎓", "type": "support",
            "title": "Learning Support Discount",
            "detail": "70% cost reduction applied — we want to support your learning journey.",
            "value": 0,
        })
        rewards.append({
            "icon": "📚", "type": "recommendation",
            "title": "Guided Mode Suggested",
            "detail": "Try our guided tutorials before attempting advanced labs.",
            "value": 0,
        })

    return rewards


# ─── 5. Misuse Detection ───────────────────────────────────────────────────────

def _detect_misuse(score, time_taken, attempts, efficiency):
    """Detect potential resource misuse or inefficiency patterns."""
    flags = []

    if attempts >= 5:
        flags.append({
            "icon": "🔴", "severity": "warning",
            "title": "High Retry Count",
            "detail": f"You used {attempts} attempts. This consumes extra resources. Review theory before retrying.",
            "action": "Billing reduced to 30% of base cost to support learning.",
        })

    if score < 30 and time_taken > 50:
        flags.append({
            "icon": "🟡", "severity": "caution",
            "title": "Low Performance Detected",
            "detail": "Low score with high time indicates possible confusion. Guided mode recommended.",
            "action": "Consider starting with a simpler topic or reviewing prerequisite material.",
        })

    if score < 20 and attempts >= 4:
        flags.append({
            "icon": "🔴", "severity": "alert",
            "title": "Resource Wastage Pattern",
            "detail": "Multiple failed attempts with very low scores. Resources are being consumed without learning progress.",
            "action": "Billing capped at minimum. Switch to guided tutorial mode for better results.",
        })

    if efficiency["efficiency_score"] < 25:
        flags.append({
            "icon": "⚠️", "severity": "info",
            "title": "Below Minimum Efficiency",
            "detail": "Your efficiency score is very low. The system has applied maximum cost protection.",
            "action": "All cost savings applied automatically. Focus on smaller, targeted exercises.",
        })

    return flags


# ─── 6. Billing Summary for History ────────────────────────────────────────────

def get_billing_summary_text(billing):
    """Generate a one-line billing summary for storage."""
    eff = billing["efficiency"]
    return (
        f"Base: ${billing['total_base_cost']} | "
        f"Efficiency: {eff['level']} ({eff['efficiency_score']}) | "
        f"Final: ${billing['final_cost']} | "
        f"Saved: ${billing['savings']} ({billing['savings_pct']}%)"
    )


def get_estimated_cost(tier_key, duration_min):
    """Calculate estimated cost for a specific tier and duration."""
    from cloud_knowledge import RESOURCE_TIERS
    tier = RESOURCE_TIERS.get(tier_key, RESOURCE_TIERS["Beginner"])
    rate_hr = tier["rate_per_hour"]
    cost = (rate_hr / 60.0) * duration_min
    return round(cost, 4)


def get_cost_simulation(goal_key, skill_level):
    """
    Generate a 'What-If' simulation comparing predicted tier vs optimized.
    """
    from cloud_knowledge import LEARNING_GOALS, RESOURCE_TIERS
    
    goal = LEARNING_GOALS.get(goal_key)
    if not goal:
        return None
        
    duration = goal["estimated_time"]
    
    # Current (Predicted)
    current_tier_key = skill_level
    current_cost = get_estimated_cost(current_tier_key, duration)
    current_tier = RESOURCE_TIERS[current_tier_key]
    
    # Optimized (Cheaper)
    if current_tier_key == "Advanced":
        opt_tier_key = "Intermediate"
    elif current_tier_key == "Intermediate":
        opt_tier_key = "Beginner"
    else:
        opt_tier_key = "Beginner"  # Already at lowest
        
    opt_cost = get_estimated_cost(opt_tier_key, duration)
    opt_tier = RESOURCE_TIERS[opt_tier_key]
    
    savings = round(current_cost - opt_cost, 4)
    savings_pct = int(round((savings / current_cost) * 100, 0)) if current_cost > 0 else 0
    
    return {
        "goal_title": goal["title"],
        "duration": duration,
        "current": {
            "tier": current_tier_key,
            "instance": current_tier["instance_type"],
            "cost": current_cost
        },
        "optimal": {
            "tier": opt_tier_key,
            "instance": opt_tier["instance_type"],
            "cost": opt_cost
        },
        "savings": savings,
        "savings_pct": savings_pct,
        "is_optimal": current_tier_key == opt_tier_key
    }


def get_all_resources():
    """Return full resource catalog for display."""
    return RESOURCE_CATALOG
