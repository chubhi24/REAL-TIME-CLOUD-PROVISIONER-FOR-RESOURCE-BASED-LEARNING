# Quick Reference: Database & API

## Database Tables

### 1. tasks
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_key TEXT NOT NULL,              -- e.g., "ec2", "s3"
    task_name TEXT NOT NULL,             -- e.g., "Launch EC2 instance"
    task_description TEXT,               -- Optional description
    task_order INTEGER NOT NULL,         -- Display order (1, 2, 3...)
    created_at TIMESTAMP,
    UNIQUE(goal_key, task_name)
);

Example rows:
| id | goal_key | task_name                   | task_order |
|----|----------|-----------------------------|----|
| 1  | ec2      | Launch an EC2 instance      | 1  |
| 2  | ec2      | Configure security group    | 2  |
| 3  | ec2      | Connect to instance via SSH | 3  |
| 4  | ec2      | Enable CloudWatch monitor   | 4  |
```

### 2. task_sessions
```sql
CREATE TABLE task_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,           -- Foreign key to users
    goal_key TEXT NOT NULL,             -- e.g., "ec2"
    goal_title TEXT NOT NULL,           -- e.g., "Launch EC2 Instance"
    session_start TIMESTAMP,            -- When session created
    session_end TIMESTAMP,              -- When session finalized
    tasks_completed INTEGER DEFAULT 0,  -- Count of completed tasks
    tasks_total INTEGER DEFAULT 0,      -- Total tasks for goal
    final_score INTEGER DEFAULT 0,      -- Calculated score (0-100)
    time_taken_seconds INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,         -- Total attempts sum
    skill_level TEXT,                   -- "Beginner"/"Intermediate"/"Advanced"
    created_at TIMESTAMP
);

Example rows:
| id | user_id | goal_key | tasks_completed | tasks_total | final_score | skill_level |
|----|---------|----------|-----------------|-------------|-------------|-------------|
| 1  | 5       | ec2      | 4               | 4           | 100         | Intermediate    |
| 2  | 5       | s3       | 3               | 4           | 75          | Beginner        |
```

### 3. task_completions
```sql
CREATE TABLE task_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_session_id INTEGER NOT NULL,   -- Foreign key to task_sessions
    user_id INTEGER NOT NULL,           -- Foreign key to users
    task_id INTEGER NOT NULL,           -- Foreign key to tasks
    task_name TEXT NOT NULL,            -- Denormalized for quick access
    completed_at TIMESTAMP,             -- When task was completed
    attempts_before_completion INTEGER DEFAULT 1,  -- Retry count
    time_to_complete_seconds INTEGER DEFAULT 0
);

Example rows:
| id | task_session_id | user_id | task_id | task_name | completed_at |
|----|-----------------|---------|---------|-----------|--------------|
| 1  | 1               | 5       | 1       | Launch ... | 2024-03-24   |
| 2  | 1               | 5       | 2       | Configure | 2024-03-24   |
| 3  | 1               | 5       | 3       | Connect   | 2024-03-24   |
| 4  | 1               | 5       | 4       | Enable    | 2024-03-24   |
```

---

## Database Functions

### Task Management

**`create_tasks_for_goal(goal_key, task_list)`**
```python
# Input:  goal_key="ec2", task_list=["Launch instance", "Configure security..."]
# Action: Stores tasks in database
# Return: True/False
```

**`get_tasks_for_goal(goal_key)`**
```python
# Input:  goal_key="ec2"
# Return: List of task rows from database
# Usage:  tasks = get_tasks_for_goal("ec2")
```

### Session Management

**`start_task_session(user_id, goal_key, goal_title)`**
```python
# Input:  user_id=5, goal_key="ec2", goal_title="Launch EC2 Instance"
# Action: Creates new row in task_sessions
# Return: session_id (to use in subsequent calls)
```

**`get_task_session(session_id)`**
```python
# Input:  session_id=123
# Return: Row with session details
# Usage:  session = get_task_session(123)
```

**`mark_task_completed(session_id, user_id, task_id, task_name, attempts)`**
```python
# Input:  session_id=123, user_id=5, task_id=1, task_name="Launch...", attempts=1
# Action: Records completion + updates session task count
# Side Effects: Updates task_sessions.tasks_completed
```

**`get_task_completions(session_id)`**
```python
# Input:  session_id=123
# Return: List of all task_completions for this session
# Usage:  Retrieve all completed tasks with timestamps
```

### Metrics & Finalization

**`calculate_session_metrics(session_id)`**
```python
# Input:  session_id=123
# Return: {
#   "score": 100,           # (tasks_completed / tasks_total) × 100
#   "tasks_completed": 4,
#   "tasks_total": 4,
#   "attempts": 3           # sum of attempts
# }
```

**`finalize_task_session(session_id, skill_level)`**
```python
# Input:  session_id=123, skill_level="Intermediate"
# Action: Sets session_end, final_score, skill_level
# Return: True/False
```

---

## API Endpoints

### 1. GET /api/session/tasks/<session_id>
Retrieve tasks for a learning session

**Request:**
```
GET /api/session/tasks/123
Authorization: User must own session
```

**Response (200 OK):**
```json
{
  "session_id": 123,
  "goal_key": "ec2",
  "goal_title": "Launch EC2 Instance",
  "tasks_completed": 2,
  "tasks_total": 4,
  "tasks": [
    {"id": 1, "name": "Launch an EC2 instance", "completed": true},
    {"id": 2, "name": "Configure security group", "completed": true},
    {"id": 3, "name": "Connect to instance via SSH", "completed": false},
    {"id": 4, "name": "Enable CloudWatch monitoring", "completed": false}
  ]
}
```

**Error Responses:**
```json
401: {"error": "Unauthorized"}
404: {"error": "Not found"}
```

---

### 2. POST /api/task/complete
Mark a task as completed

**Request:**
```
POST /api/task/complete
Content-Type: application/json
Authorization: User must own session

{
  "session_id": 123,
  "task_name": "Launch an EC2 instance",
  "attempts": 1
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "session_id": 123,
  "tasks_completed": 2,
  "tasks_total": 4,
  "progress_pct": 50
}
```

**Side Effects:**
- Creates record in task_completions table
- Updates task_sessions.tasks_completed
- Returns updated progress

---

### 3. GET /api/session/progress/<session_id>
Get current progress for a session

**Request:**
```
GET /api/session/progress/123
Authorization: User must own session
```

**Response (200 OK):**
```json
{
  "session_id": 123,
  "tasks_completed": 2,
  "tasks_total": 4,
  "progress_pct": 50,
  "metrics": {
    "score": 50,
    "attempts": 2
  }
}
```

---

### 4. POST /api/session/finalize
Finalize session and calculate skill level

**Request:**
```
POST /api/session/finalize
Content-Type: application/json
Authorization: User must own session

{
  "session_id": 123
}
```

**Response (200 OK):**
```json
{
  "success": true,
  "session_id": 123,
  "skill_level": "Intermediate",
  "confidence": 87.3,
  "score": 75,
  "attempts": 3
}
```

**Process:**
1. Calculates metrics from task completions
2. Runs ML model with (score, time, attempts)
3. Updates task_sessions with results
4. Returns skill prediction

---

## Task Definitions

### All Goals (as of March 2024)

**EC2: Launch EC2 Instance** (4 tasks)
1. Launch an EC2 instance
2. Configure security group
3. Connect to instance via SSH
4. Enable CloudWatch monitoring

**S3: Store Data in S3** (4 tasks)
1. Create S3 bucket
2. Set bucket permissions
3. Upload files to bucket
4. Enable versioning

**CloudWatch: Monitor Application** (4 tasks)
1. Explore default metrics
2. Create custom metrics
3. Setup alarms
4. Configure SNS notifications

**Web App: Deploy Web Application** (5 tasks)
1. Launch and configure EC2 instance
2. Install web server
3. Setup RDS database
4. Deploy application code
5. Configure domain and SSL

**Load Balancer: Setup Load Balancer** (5 tasks)
1. Launch multiple EC2 instances
2. Create target group
3. Create Application Load Balancer
4. Configure health checks
5. Test failover scenario

**Serverless: Build Serverless Application** (6 tasks)
1. Create IAM role
2. Write Lambda function
3. Setup API Gateway
4. Create DynamoDB table
5. Connect Lambda to DynamoDB
6. Setup S3 event triggers

---

## Score Mapping

| Score | Completion | Interpretation |
|-------|-----------|-----------------|
| 100% | 4/4 tasks | Complete mastery |
| 75% | 3/4 tasks | Strong performance |
| 50% | 2/4 tasks | Adequate completion |
| 25% | 1/4 tasks | Minimal progress |
| 0% | 0/4 tasks | No progress |

---

## Example Workflow (SQL)

```sql
-- 1. User starts EC2 goal (user_id=5)
INSERT INTO task_sessions 
(user_id, goal_key, goal_title, tasks_total)
VALUES (5, 'ec2', 'Launch EC2 Instance', 4);
-- Result: session_id = 123

-- 2. Create tasks for EC2 goal (if not exists)
INSERT INTO tasks (goal_key, task_name, task_order)
VALUES ('ec2', 'Launch an EC2 instance', 1);
-- ... repeat for other 3 tasks

-- 3. User completes first task
INSERT INTO task_completions 
(task_session_id, user_id, task_id, task_name, attempts_before_completion)
VALUES (123, 5, 1, 'Launch an EC2 instance', 1);
UPDATE task_sessions SET tasks_completed = 1 WHERE id = 123;

-- 4. User completes second task
INSERT INTO task_completions 
(task_session_id, user_id, task_id, task_name, attempts_before_completion)
VALUES (123, 5, 2, 'Configure security group', 1);
UPDATE task_sessions SET tasks_completed = 2 WHERE id = 123;

-- ... repeat for tasks 3 & 4

-- 5. User finalizes session
-- Calculate: score = (4/4) * 100 = 100
-- Predict: skill_level = "Intermediate" (confidence 87.3%)
UPDATE task_sessions 
SET session_end = NOW(), 
    final_score = 100,
    attempts = 4,
    skill_level = 'Intermediate'
WHERE id = 123;

-- 6. Save to old results table (backward compatible)
INSERT INTO results 
(user_id, username, score, time_taken, attempts, skill_level, 
 difficulty, cpu, ram, gpu, cost, notes)
VALUES (5, 'user5', 100, 32, 4, 'Intermediate', 'Beginner',
        '4 vCPU', '8 GB', 'Shared GPU', 0.08, 'Task-based');
```

---

## Frontend Integration

### JavaScript to Call APIs

```javascript
// 1. Get tasks for session
fetch('/api/session/tasks/123')
  .then(r => r.json())
  .then(data => console.log(data.tasks));

// 2. Mark task complete
fetch('/api/task/complete', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    session_id: 123,
    task_name: 'Launch an EC2 instance',
    attempts: 1
  })
})
.then(r => r.json())
.then(data => updateProgressBar(data.progress_pct));

// 3. Get progress
fetch('/api/session/progress/123')
  .then(r => r.json())
  .then(data => updateUI(data.metrics));

// 4. Finalize session
fetch('/api/session/finalize', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({session_id: 123})
})
.then(r => r.json())
.then(data => showResults(data));
```

---

## Debugging Tips

### Check Session Status
```sql
SELECT * FROM task_sessions WHERE id = 123;
-- Look at: tasks_completed, tasks_total, final_score, skill_level
```

### Check Task Completions
```sql
SELECT * FROM task_completions WHERE task_session_id = 123;
-- Should have N rows equal to tasks_completed
```

### Verify Score Calculation
```python
from db import calculate_session_metrics
metrics = calculate_session_metrics(123)
print(f"Score: {metrics['score']}%")
print(f"Tasks: {metrics['tasks_completed']}/{metrics['tasks_total']}")
```

### Check API Response
```javascript
// Open browser DevTools (F12)
// Go to Network tab
// Click on API request (e.g., POST /api/task/complete)
// Check Response tab for returned JSON
```

---

## Performance

| Operation | Time | Notes |
|-----------|------|-------|
| Get tasks | ~5ms | Simple query |
| Mark task complete | ~50ms | Includes update |
| Get progress | ~10ms | Cached calculations |
| Finalize session | ~150ms | Includes ML prediction |
| Database per-query | <5ms | Well-indexed |

---

## Related Routes

### Learning (unchanged)
- GET `/learn` - List goals
- POST `/learn/start` - Create session (MODIFIED)
- GET `/api/cost_simulation/<goal>` - Cost simulation

### Prediction (backward compatible)
- POST `/predict` - Save manual results
- Used by task system via hidden form

### Dashboard (unchanged)
- GET `/dashboard` - Display results

---

## Backward Compatibility

✅ **Old routes still work:**
- Manual `/predict` endpoint unchanged
- `learning_sessions` table still populated
- `results` table format unchanged
- Can mix old and new results

✅ **Optional migration:**
- No force migration required
- Users choose task-based or manual
- Results appear mixed in dashboard
- Gradual adoption possible

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-03-24 | Initial release with task system |
| 0.9 | 2024-03-20 | Beta testing |
| 0.8 | 2024-03-10 | Development |

---

**Last Updated:** March 24, 2024  
**Maintainer:** Development Team  
**Status:** Production Ready
