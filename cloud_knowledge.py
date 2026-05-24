# ═══════════════════════════════════════════════════════════════════════════════
# Cloud Knowledge Mapping Engine — Intelligent Cloud Learning & Simulation
# ═══════════════════════════════════════════════════════════════════════════════
import random

# ─── 1. Learning Goals ──────────────────────────────────────────────────────────

LEARNING_GOALS = {
    "ec2": {
        "title": "Launch EC2 Instance",
        "icon": "🖥️",
        "description": "Learn to provision and manage virtual servers on AWS.",
        "components": ["EC2 Instance", "Key Pair", "Security Group", "VPC", "CloudWatch"],
        "base_difficulty": "Beginner",
        "category": "Compute",
        "estimated_time": 30,
    },
    "s3": {
        "title": "Store Data in S3",
        "icon": "🪣",
        "description": "Master object storage with buckets, policies, and versioning.",
        "components": ["S3 Bucket", "IAM Policy", "Bucket Policy", "CloudFront CDN"],
        "base_difficulty": "Beginner",
        "category": "Storage",
        "estimated_time": 20,
    },
    "cloudwatch": {
        "title": "Monitor Application (CloudWatch)",
        "icon": "📊",
        "description": "Set up metrics, alarms, dashboards, and log insights.",
        "components": ["CloudWatch Metrics", "CloudWatch Alarms", "SNS Notifications",
                       "CloudWatch Logs", "CloudWatch Dashboards"],
        "base_difficulty": "Intermediate",
        "category": "Monitoring",
        "estimated_time": 40,
    },
    "webapp": {
        "title": "Deploy Web Application",
        "icon": "🌐",
        "description": "Deploy a full web application using Elastic Beanstalk or EC2 + RDS.",
        "components": ["EC2 / Elastic Beanstalk", "RDS (MySQL/PostgreSQL)",
                       "S3 (Static Assets)", "Route 53 (DNS)", "ACM (SSL)",
                       "ALB (Load Balancer)"],
        "base_difficulty": "Intermediate",
        "category": "Full Stack",
        "estimated_time": 60,
    },
    "loadbalancer": {
        "title": "Setup Load Balancer",
        "icon": "⚖️",
        "description": "Configure Application Load Balancer with target groups and health checks.",
        "components": ["Application Load Balancer", "Target Group", "Auto Scaling Group",
                       "EC2 Instances", "Health Checks", "Security Groups"],
        "base_difficulty": "Intermediate",
        "category": "Networking",
        "estimated_time": 45,
    },
    "serverless": {
        "title": "Build Serverless Application",
        "icon": "⚡",
        "description": "Create event-driven apps with Lambda, API Gateway, and DynamoDB.",
        "components": ["AWS Lambda", "API Gateway", "DynamoDB", "S3 Triggers",
                       "CloudWatch Logs", "IAM Roles", "SAM / CloudFormation"],
        "base_difficulty": "Advanced",
        "category": "Serverless",
        "estimated_time": 75,
    },
}

# ─── 1.5. Task-Based Learning Checklists ────────────────────────────────────────

TASK_DEFINITIONS = {
    "ec2": [
        "Launch an EC2 instance",
        "Configure security group",
        "Connect to instance via SSH",
        "Enable CloudWatch monitoring",
    ],
    "s3": [
        "Create S3 bucket",
        "Set bucket permissions",
        "Upload files to bucket",
        "Enable versioning",
    ],
    "cloudwatch": [
        "Explore default metrics",
        "Create custom metrics",
        "Setup alarms",
        "Configure SNS notifications",
    ],
    "webapp": [
        "Launch and configure EC2 instance",
        "Install web server",
        "Setup RDS database",
        "Deploy application code",
        "Configure domain and SSL",
    ],
    "loadbalancer": [
        "Launch multiple EC2 instances",
        "Create target group",
        "Create Application Load Balancer",
        "Configure health checks",
        "Test failover scenario",
    ],
    "serverless": [
        "Create IAM role",
        "Write Lambda function",
        "Setup API Gateway",
        "Create DynamoDB table",
        "Connect Lambda to DynamoDB",
        "Setup S3 event triggers",
    ],
}

# ─── 2. Skill-Based Resource Tiers ──────────────────────────────────────────────

RESOURCE_TIERS = {
    "Beginner": {
        "instance_type": "t2.micro",
        "cpu": "1 vCPU",
        "ram": "1 GB",
        "gpu": "None",
        "region": "ap-south-1 (Mumbai)",
        "rate_per_hour": 0.02,
    },
    "Intermediate": {
        "instance_type": "t2.medium",
        "cpu": "4 vCPU",
        "ram": "8 GB",
        "gpu": "Shared GPU",
        "region": "ap-south-1 (Mumbai)",
        "rate_per_hour": 0.08,
    },
    "Advanced": {
        "instance_type": "t2.large",
        "cpu": "8 vCPU",
        "ram": "16 GB",
        "gpu": "Dedicated GPU",
        "region": "ap-south-1 (Mumbai)",
        "rate_per_hour": 0.20,
    },
}

# ─── 3. Learning Roadmaps ──────────────────────────────────────────────────────

ROADMAPS = {
    "ec2": [
        {"step": 1, "title": "Create VPC & Subnet",          "difficulty": "Beginner",     "time": 5,  "desc": "Set up a Virtual Private Cloud with public subnet."},
        {"step": 2, "title": "Generate Key Pair",             "difficulty": "Beginner",     "time": 3,  "desc": "Create an SSH key pair for secure instance access."},
        {"step": 3, "title": "Configure Security Group",      "difficulty": "Beginner",     "time": 5,  "desc": "Define inbound/outbound rules for SSH, HTTP, HTTPS."},
        {"step": 4, "title": "Launch EC2 Instance",            "difficulty": "Beginner",     "time": 7,  "desc": "Select AMI, instance type, and launch the instance."},
        {"step": 5, "title": "Connect via SSH",                "difficulty": "Intermediate", "time": 5,  "desc": "Use your key pair to SSH into the running instance."},
        {"step": 6, "title": "Setup CloudWatch Monitoring",    "difficulty": "Intermediate", "time": 5,  "desc": "Enable detailed monitoring and set CPU alarms."},
    ],
    "s3": [
        {"step": 1, "title": "Create S3 Bucket",              "difficulty": "Beginner",     "time": 3,  "desc": "Create a new bucket with a unique name."},
        {"step": 2, "title": "Configure Access Permissions",  "difficulty": "Beginner",     "time": 4,  "desc": "Set bucket policy and ACLs for access control."},
        {"step": 3, "title": "Upload Objects",                 "difficulty": "Beginner",     "time": 3,  "desc": "Upload files via console or AWS CLI."},
        {"step": 4, "title": "Enable Versioning",              "difficulty": "Intermediate", "time": 3,  "desc": "Turn on versioning for data protection."},
        {"step": 5, "title": "Configure Lifecycle Policies",   "difficulty": "Intermediate", "time": 4,  "desc": "Auto-transition objects to Glacier for cost savings."},
        {"step": 6, "title": "Setup CloudFront CDN",           "difficulty": "Advanced",     "time": 5,  "desc": "Distribute content globally with low latency."},
    ],
    "cloudwatch": [
        {"step": 1, "title": "Explore Default Metrics",       "difficulty": "Beginner",     "time": 5,  "desc": "Navigate CloudWatch console and view EC2 metrics."},
        {"step": 2, "title": "Create Custom Metrics",          "difficulty": "Intermediate", "time": 8,  "desc": "Push custom application metrics using SDK."},
        {"step": 3, "title": "Setup Alarms",                   "difficulty": "Intermediate", "time": 7,  "desc": "Create alarms for CPU, memory, and custom thresholds."},
        {"step": 4, "title": "Configure SNS Notifications",    "difficulty": "Intermediate", "time": 5,  "desc": "Setup email/SMS alerts when alarms trigger."},
        {"step": 5, "title": "Build Dashboards",               "difficulty": "Advanced",     "time": 8,  "desc": "Create visual dashboards with multiple widgets."},
        {"step": 6, "title": "Use Log Insights",               "difficulty": "Advanced",     "time": 7,  "desc": "Query and analyze application logs with Insights."},
    ],
    "webapp": [
        {"step": 1, "title": "Launch EC2 Instance",            "difficulty": "Beginner",     "time": 7,  "desc": "Provision a compute instance for your web server."},
        {"step": 2, "title": "Configure Security Groups",      "difficulty": "Beginner",     "time": 5,  "desc": "Open ports 80, 443 for HTTP/HTTPS traffic."},
        {"step": 3, "title": "Install Web Server (Nginx)",     "difficulty": "Intermediate", "time": 8,  "desc": "Install and configure Nginx as a reverse proxy."},
        {"step": 4, "title": "Setup RDS Database",             "difficulty": "Intermediate", "time": 10, "desc": "Create a managed MySQL/PostgreSQL database."},
        {"step": 5, "title": "Deploy Application Code",        "difficulty": "Intermediate", "time": 10, "desc": "Upload your app, configure environment variables."},
        {"step": 6, "title": "Configure Route53 & SSL",        "difficulty": "Advanced",     "time": 10, "desc": "Map custom domain and enable HTTPS with ACM."},
        {"step": 7, "title": "Setup CloudWatch Monitoring",    "difficulty": "Advanced",     "time": 10, "desc": "Monitor app health, set up error rate alarms."},
    ],
    "loadbalancer": [
        {"step": 1, "title": "Launch Multiple EC2 Instances",  "difficulty": "Beginner",     "time": 8,  "desc": "Create 2+ instances across availability zones."},
        {"step": 2, "title": "Create Target Group",            "difficulty": "Intermediate", "time": 7,  "desc": "Define target group with health check configuration."},
        {"step": 3, "title": "Create Application Load Balancer","difficulty": "Intermediate","time": 8,  "desc": "Setup ALB with listeners on port 80/443."},
        {"step": 4, "title": "Configure Health Checks",        "difficulty": "Intermediate", "time": 5,  "desc": "Define health check path and thresholds."},
        {"step": 5, "title": "Setup Auto Scaling",             "difficulty": "Advanced",     "time": 10, "desc": "Create launch template and scaling policies."},
        {"step": 6, "title": "Test Failover",                  "difficulty": "Advanced",     "time": 7,  "desc": "Simulate instance failure and verify recovery."},
    ],
    "serverless": [
        {"step": 1, "title": "Create IAM Role for Lambda",    "difficulty": "Beginner",     "time": 5,  "desc": "Create execution role with necessary permissions."},
        {"step": 2, "title": "Write Lambda Function",          "difficulty": "Intermediate", "time": 10, "desc": "Create a Python/Node.js function with handler."},
        {"step": 3, "title": "Setup API Gateway",              "difficulty": "Intermediate", "time": 10, "desc": "Create REST API with routes mapped to Lambda."},
        {"step": 4, "title": "Create DynamoDB Table",          "difficulty": "Intermediate", "time": 8,  "desc": "Design table with partition key and sort key."},
        {"step": 5, "title": "Connect Lambda to DynamoDB",     "difficulty": "Advanced",     "time": 10, "desc": "Read/write from DynamoDB within Lambda function."},
        {"step": 6, "title": "Setup S3 Event Triggers",        "difficulty": "Advanced",     "time": 8,  "desc": "Trigger Lambda on S3 object upload events."},
        {"step": 7, "title": "Deploy with SAM",                "difficulty": "Advanced",     "time": 14, "desc": "Package and deploy using Serverless Application Model."},
    ],
}

# ─── 4. Error Scenarios ─────────────────────────────────────────────────────────

ERROR_SCENARIOS = {
    "ec2": [
        {"code": "EC2-001", "error": "Instance Unreachable", "cause": "Missing Key Pair — no SSH key was associated with the instance.", "fix": "Create a new key pair, terminate the instance, and relaunch with the key pair attached.", "severity": "Critical"},
        {"code": "EC2-002", "error": "SSH Connection Refused", "cause": "Security Group has Port 22 closed — inbound SSH traffic blocked.", "fix": "Edit Security Group inbound rules: Add rule for SSH (port 22) from your IP.", "severity": "High"},
        {"code": "EC2-003", "error": "Permission Denied (publickey)", "cause": "Wrong username or corrupted key pair file.", "fix": "Use the correct username (ec2-user, ubuntu) and verify .pem file permissions (chmod 400).", "severity": "Medium"},
        {"code": "EC2-004", "error": "Instance Stuck in Pending", "cause": "Insufficient capacity in the selected Availability Zone.", "fix": "Try launching in a different AZ or use a different instance type.", "severity": "Medium"},
    ],
    "s3": [
        {"code": "S3-001", "error": "Access Denied (403)", "cause": "Bucket policy denies access — IAM user lacks s3:GetObject permission.", "fix": "Update IAM policy to include s3:GetObject or modify bucket policy.", "severity": "High"},
        {"code": "S3-002", "error": "Bucket Already Exists", "cause": "S3 bucket names are globally unique — name already taken.", "fix": "Choose a different, unique bucket name (e.g., add date suffix).", "severity": "Low"},
        {"code": "S3-003", "error": "NoSuchKey Error", "cause": "Attempting to download a non-existent object key.", "fix": "Verify the object key path. Check for typos and correct casing.", "severity": "Medium"},
    ],
    "cloudwatch": [
        {"code": "CW-001", "error": "No Data Points in Metrics", "cause": "Detailed monitoring not enabled — only 5-min intervals available.", "fix": "Enable detailed monitoring on EC2 instance for 1-minute intervals.", "severity": "Medium"},
        {"code": "CW-002", "error": "Alarm Stuck in INSUFFICIENT_DATA", "cause": "CloudWatch hasn't received enough data points to evaluate.", "fix": "Wait for evaluation period or check metric name/namespace.", "severity": "Low"},
        {"code": "CW-003", "error": "SNS Notification Not Received", "cause": "SNS subscription not confirmed — email confirmation pending.", "fix": "Check inbox for AWS SNS confirmation email and click confirm.", "severity": "High"},
    ],
    "webapp": [
        {"code": "WA-001", "error": "502 Bad Gateway", "cause": "Nginx cannot connect to upstream application server.", "fix": "Verify app is running on the configured port. Check Nginx proxy_pass.", "severity": "Critical"},
        {"code": "WA-002", "error": "Database Connection Timeout", "cause": "RDS Security Group doesn't allow inbound from EC2.", "fix": "Add EC2 security group as source in RDS inbound rules on port 3306.", "severity": "Critical"},
        {"code": "WA-003", "error": "SSL Certificate Error", "cause": "ACM certificate not validated — DNS record not added.", "fix": "Add the CNAME record from ACM to your Route53 hosted zone.", "severity": "High"},
        {"code": "WA-004", "error": "Static Assets Not Loading", "cause": "S3 bucket CORS not configured for your domain.", "fix": "Add CORS configuration to S3 bucket allowing your domain origin.", "severity": "Medium"},
    ],
    "loadbalancer": [
        {"code": "LB-001", "error": "All Targets Unhealthy", "cause": "Health check path returns 404 — incorrect health check endpoint.", "fix": "Update health check path to a valid endpoint (e.g., /health).", "severity": "Critical"},
        {"code": "LB-002", "error": "504 Gateway Timeout", "cause": "Backend instance response exceeds ALB idle timeout (60s).", "fix": "Increase ALB idle timeout or optimize backend response time.", "severity": "High"},
        {"code": "LB-003", "error": "Uneven Traffic Distribution", "cause": "Cross-zone load balancing is disabled.", "fix": "Enable cross-zone load balancing in ALB attributes.", "severity": "Medium"},
    ],
    "serverless": [
        {"code": "SL-001", "error": "Lambda Timeout", "cause": "Function exceeds 3-second default timeout.", "fix": "Increase timeout in function configuration (max 15 minutes).", "severity": "High"},
        {"code": "SL-002", "error": "AccessDeniedException", "cause": "Lambda execution role missing required IAM permissions.", "fix": "Attach the needed policy (e.g., AmazonDynamoDBFullAccess) to the role.", "severity": "Critical"},
        {"code": "SL-003", "error": "API Gateway 500 Error", "cause": "Lambda returns invalid response format for API Gateway proxy.", "fix": "Return {'statusCode': 200, 'body': json.dumps(data)} format.", "severity": "High"},
        {"code": "SL-004", "error": "Cold Start Latency", "cause": "Lambda function initialized from scratch on first invocation.", "fix": "Use provisioned concurrency or minimize package size.", "severity": "Medium"},
    ],
}

# ─── 5. Cost Optimization Suggestions ───────────────────────────────────────────

COST_OPTIMIZATION = {
    "Beginner": {
        "current": {"instance": "t2.micro", "cost_hr": 0.02, "monthly": 14.40},
        "optimal": {"instance": "t2.micro", "cost_hr": 0.02, "monthly": 14.40},
        "savings_pct": 0,
        "suggestions": [
            "You're already on the most cost-effective tier!",
            "Consider using AWS Free Tier for 12 months of free t2.micro.",
            "Schedule instance stop during non-learning hours to save costs.",
        ],
    },
    "Intermediate": {
        "current": {"instance": "t2.medium", "cost_hr": 0.08, "monthly": 57.60},
        "optimal": {"instance": "t2.small", "cost_hr": 0.04, "monthly": 28.80},
        "savings_pct": 50,
        "suggestions": [
            "Downgrade to t2.small — sufficient for most intermediate labs.",
            "Use Spot Instances for non-critical workloads (save up to 90%).",
            "Enable auto-stop after 30 minutes of inactivity.",
            "Consider Reserved Instances for long-term learning paths.",
        ],
    },
    "Advanced": {
        "current": {"instance": "t2.large", "cost_hr": 0.20, "monthly": 144.00},
        "optimal": {"instance": "t2.medium", "cost_hr": 0.08, "monthly": 57.60},
        "savings_pct": 60,
        "suggestions": [
            "Downgrade to t2.medium for tasks not requiring 16GB RAM.",
            "Use Spot Instances for batch processing and testing (saves ~90%).",
            "Leverage AWS Savings Plans for committed usage discounts.",
            "Use Graviton (ARM-based) instances — 20% cheaper with better perf.",
            "Schedule workloads during off-peak hours for lower spot pricing.",
        ],
    },
}

# ─── 6. AI Coach Feedback Rules ─────────────────────────────────────────────────

def generate_ai_coaching(avg_score, avg_time, avg_attempts, skill_level, goal_key):
    """Generate personalized AI coaching feedback based on user performance."""
    feedback = []
    goal = LEARNING_GOALS.get(goal_key, {})
    goal_title = goal.get("title", "this topic")

    # Score analysis
    if avg_score >= 85:
        feedback.append({
            "icon": "🏆", "type": "strength",
            "msg": f"Excellent mastery! Your avg score of {avg_score:.0f} shows strong understanding of {goal_title}."
        })
    elif avg_score >= 60:
        feedback.append({
            "icon": "📈", "type": "improvement",
            "msg": f"Your avg score of {avg_score:.0f} is good but there's room for improvement. Review weak areas."
        })
    else:
        feedback.append({
            "icon": "📚", "type": "attention",
            "msg": f"Your avg score of {avg_score:.0f} suggests you need more practice. Start with foundational concepts."
        })

    # Speed analysis
    if avg_time <= 15:
        feedback.append({
            "icon": "⚡", "type": "strength",
            "msg": "You're very fast! But verify you're not rushing through important details."
        })
    elif avg_time <= 40:
        feedback.append({
            "icon": "⏱️", "type": "neutral",
            "msg": f"Your avg time of {avg_time:.0f}min is within optimal range. Good pacing!"
        })
    else:
        feedback.append({
            "icon": "🐢", "type": "improvement",
            "msg": f"Avg time of {avg_time:.0f}min is high. Try breaking tasks into smaller chunks."
        })

    # Attempts analysis
    if avg_attempts <= 2:
        feedback.append({
            "icon": "🎯", "type": "strength",
            "msg": "Low avg attempts — you learn efficiently with minimal retries!"
        })
    elif avg_attempts <= 4:
        feedback.append({
            "icon": "🔄", "type": "improvement",
            "msg": f"Avg {avg_attempts:.1f} attempts — focus on understanding errors before retrying."
        })
    else:
        feedback.append({
            "icon": "⚠️", "type": "attention",
            "msg": f"High avg attempts ({avg_attempts:.1f}). Review theory before hands-on practice to reduce trial-and-error."
        })

    # Skill-specific advice
    if skill_level == "Beginner":
        feedback.append({
            "icon": "🌱", "type": "guidance",
            "msg": f"As a beginner, complete the full roadmap for {goal_title} step-by-step before exploring advanced topics."
        })
    elif skill_level == "Intermediate":
        feedback.append({
            "icon": "🚀", "type": "guidance",
            "msg": "You're ready for real-world scenarios. Try combining multiple services in a mini-project."
        })
    else:
        feedback.append({
            "icon": "💎", "type": "guidance",
            "msg": "At advanced level, focus on optimization, cost management, and architectural best practices."
        })

    # Efficiency score
    efficiency = max(0, min(100, int(avg_score - (avg_attempts * 5) - (avg_time * 0.3))))
    feedback.append({
        "icon": "📊", "type": "metric",
        "msg": f"Your Learning Efficiency Score: {efficiency}/100 (based on score, speed, and attempt balance)."
    })

    return feedback


# ─── 7. AI Guidance Tips (per goal + skill) ────────────────────────────────────

GUIDANCE = {
    "ec2": {
        "Beginner": [
            "Start with a t2.micro — it's free-tier eligible.",
            "Practice connecting via SSH before configuring services.",
            "Always set up Security Groups before launching instances.",
        ],
        "Intermediate": [
            "Explore Elastic IPs and multiple availability zones.",
            "Set up CloudWatch alarms for CPU utilization monitoring.",
            "Try creating custom AMIs from your configured instances.",
        ],
        "Advanced": [
            "Implement auto-scaling policies with launch templates.",
            "Use spot instances to reduce costs by up to 90%.",
            "Integrate with Systems Manager for fleet management.",
        ],
    },
    "s3": {
        "Beginner": [
            "Create your first bucket and upload files via the console.",
            "Learn the difference between public and private access.",
            "Enable versioning to protect against accidental deletions.",
        ],
        "Intermediate": [
            "Configure lifecycle policies to transition objects to Glacier.",
            "Set up cross-region replication for disaster recovery.",
            "Use presigned URLs for secure temporary access.",
        ],
        "Advanced": [
            "Implement S3 event notifications with Lambda triggers.",
            "Use S3 Select/Athena for in-place querying of data lakes.",
            "Optimize costs using Intelligent-Tiering storage class.",
        ],
    },
    "cloudwatch": {
        "Beginner": [
            "Start by exploring the default EC2 metrics dashboard.",
            "Create a simple CPU utilization alarm to learn the basics.",
            "Use CloudWatch Logs to monitor application output.",
        ],
        "Intermediate": [
            "Build custom dashboards with multiple metric widgets.",
            "Configure composite alarms for complex monitoring.",
            "Use Log Insights to query and analyze log patterns.",
        ],
        "Advanced": [
            "Implement anomaly detection for proactive monitoring.",
            "Create cross-account, cross-region observability setups.",
            "Use Contributor Insights for real-time traffic analysis.",
        ],
    },
    "webapp": {
        "Beginner": [
            "Start with Elastic Beanstalk for simplified deployment.",
            "Ensure your application health check endpoint is configured.",
            "Use RDS free tier for your first managed database.",
        ],
        "Intermediate": [
            "Separate static assets to S3 + CloudFront for performance.",
            "Implement blue/green deployments for zero-downtime updates.",
            "Set up Route 53 with a custom domain and SSL via ACM.",
        ],
        "Advanced": [
            "Design multi-AZ architecture with read replicas for RDS.",
            "Implement CI/CD pipelines with CodePipeline and CodeDeploy.",
            "Use ElastiCache (Redis) for session management and caching.",
        ],
    },
    "loadbalancer": {
        "Beginner": [
            "Start with an Application Load Balancer (ALB) — it's HTTP-aware.",
            "Create a target group with at least two EC2 instances.",
            "Configure health checks to auto-remove unhealthy targets.",
        ],
        "Intermediate": [
            "Set up path-based and host-based routing rules.",
            "Integrate ALB with Auto Scaling for elastic capacity.",
            "Use sticky sessions when your app needs session affinity.",
        ],
        "Advanced": [
            "Implement WAF rules on your ALB for DDoS protection.",
            "Configure cross-zone load balancing for even distribution.",
            "Use weighted target groups for canary/A-B deployments.",
        ],
    },
    "serverless": {
        "Beginner": [
            "Create your first Lambda with a simple API Gateway trigger.",
            "Use the AWS Console editor to test before using the CLI.",
            "Start with Python/Node.js — fastest cold starts.",
        ],
        "Intermediate": [
            "Implement DynamoDB streams with Lambda for event processing.",
            "Use SAM for local testing.",
            "Optimize Lambda memory — it also scales CPU proportionally.",
        ],
        "Advanced": [
            "Implement Step Functions for complex serverless workflows.",
            "Use Lambda Layers to share code across functions.",
            "Design event sourcing patterns with EventBridge and SQS.",
        ],
    },
}


# ─── Public API Functions ───────────────────────────────────────────────────────

def get_learning_goal(goal_key):
    return LEARNING_GOALS.get(goal_key)

def get_resource_tier(skill_level):
    return RESOURCE_TIERS.get(skill_level, RESOURCE_TIERS["Beginner"])

def get_guidance(goal_key, skill_level):
    goal_guidance = GUIDANCE.get(goal_key, {})
    return goal_guidance.get(skill_level, goal_guidance.get("Beginner", []))

def calculate_learning_cost(skill_level, estimated_time_minutes):
    tier = get_resource_tier(skill_level)
    hours = estimated_time_minutes / 60.0
    return round(tier["rate_per_hour"] * hours, 4)

def get_all_goals():
    return LEARNING_GOALS

def get_roadmap(goal_key):
    return ROADMAPS.get(goal_key, [])

def get_simulated_errors(goal_key, count=2):
    """Return random error scenarios for a given goal."""
    errors = ERROR_SCENARIOS.get(goal_key, [])
    if not errors:
        return []
    return random.sample(errors, min(count, len(errors)))

def get_cost_optimization(skill_level):
    return COST_OPTIMIZATION.get(skill_level, COST_OPTIMIZATION["Beginner"])

# ─── 8. Goal Task Checklists ────────────────────────────────────────────────────────

GOAL_TASKS = {
    "ec2": [
        "Create VPC & Subnet",
        "Generate Key Pair",
        "Configure Security Group",
        "Launch EC2 Instance",
        "Connect via SSH",
        "Setup CloudWatch Monitoring"
    ],
    "s3": [
        "Create S3 Bucket",
        "Configure Access Permissions",
        "Upload Objects",
        "Enable Versioning",
        "Configure Lifecycle Policies",
        "Setup CloudFront CDN"
    ],
    "cloudwatch": [
        "Explore Default Metrics",
        "Create Custom Metrics",
        "Setup Alarms",
        "Configure SNS Notifications",
        "Build Dashboards",
        "Use Log Insights"
    ],
    "webapp": [
        "Launch EC2 Instance",
        "Configure Security Groups",
        "Install Web Server (Nginx)",
        "Setup RDS Database",
        "Deploy Application Code",
        "Configure Route53 & SSL",
        "Setup CloudWatch Monitoring"
    ],
    "loadbalancer": [
        "Launch Multiple EC2 Instances",
        "Create Target Group",
        "Create Application Load Balancer",
        "Configure Health Checks",
        "Setup Auto Scaling",
        "Test Failover"
    ],
    "serverless": [
        "Create IAM Role for Lambda",
        "Write Lambda Function",
        "Setup API Gateway",
        "Create DynamoDB Table",
        "Connect Lambda to DynamoDB",
        "Setup S3 Event Triggers",
        "Deploy with SAM"
    ]
}

# ─── Task Management Functions ──────────────────────────────────────────────────

def get_tasks_for_goal(goal_key):
    """Get task list for a learning goal."""
    return TASK_DEFINITIONS.get(goal_key, [])
