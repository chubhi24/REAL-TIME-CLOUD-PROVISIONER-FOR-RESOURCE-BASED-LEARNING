# Task-Based Performance Tracking System
## Automatic Performance Evaluation without Manual Input

### Overview

The system has been enhanced to replace manual input fields (**score, time, attempts**) with an **automated task-based tracking system**. Users now complete a checklist of tasks, and performance is calculated automatically based on task completion.

---

## Architecture

### 1. Database Schema

#### New Tables

**`tasks`** - Defines tasks for each learning goal
```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    goal_key TEXT NOT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT,
    task_order INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(goal_key, task_name)
)
```

**`task_sessions`** - Tracks each learning session with task progress
```sql
CREATE TABLE task_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    goal_key TEXT NOT NULL,
    goal_title TEXT NOT NULL,
    session_start TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    session_end TIMESTAMP,
    tasks_completed INTEGER DEFAULT 0,
    tasks_total INTEGER DEFAULT 0,
    final_score INTEGER DEFAULT 0,
    time_taken_seconds INTEGER DEFAULT 0,
    attempts INTEGER DEFAULT 0,
    skill_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
```

**`task_completions`** - Tracks individual task completions
```sql
CREATE TABLE task_completions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_session_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    task_id INTEGER NOT NULL,
    task_name TEXT NOT NULL,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    attempts_before_completion INTEGER DEFAULT 1,
    time_to_complete_seconds INTEGER DEFAULT 0,
    FOREIGN KEY (task_session_id) REFERENCES task_sessions(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (task_id) REFERENCES tasks(id)
)
```

### 2. Task Definitions

Each learning goal now has a checklist of tasks defined in `cloud_knowledge.py`:

```python
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
    # ... more goals
}
```

---

## Key Features

### 1. Automatic Score Calculation

**Formula:**
```
Score = (Tasks Completed / Total Tasks) × 100
```

Example:
- 3 out of 4 tasks completed = 75%
- 4 out of 4 tasks completed = 100%

### 2. Automatic Time Tracking

- Session start time is recorded when `/learn/start` is called
- Session end time is recorded when user finalizes the session
- Time is automatically calculated from these timestamps

### 3. Hidden Attempt Tracking

- Each task completion records the number of attempts
- Attempts are summed across all tasks in a session
- Users are not asked to input attempts manually

### 4. Task Checklist UI

The learning page now displays:
- ✅ Interactive task checklist with checkboxes
- 📊 Real-time progress bar showing completion percentage
- 🎯 Visual feedback when tasks are completed
- 🏁 "Complete Learning Session" button (enabled when all tasks done)

### 5. Automatic Skill Prediction

When a session is finalized:
1. Metrics are calculated from task data (score, time, attempts)
2. ML model predicts skill level based on metrics
3. Confidence score is provided alongside skill prediction

---

## API Endpoints

### `/api/session/tasks/<session_id>`
**GET** - Retrieve tasks for a learning session

**Response:**
```json
{
    "session_id": 123,
    "goal_key": "ec2",
    "goal_title": "Launch EC2 Instance",
    "tasks": [
        {"id": 1, "name": "Launch an EC2 instance", "completed": false},
        {"id": 2, "name": "Configure security group", "completed": true}
    ],
    "tasks_completed": 1,
    "tasks_total": 4
}
```

### `/api/task/complete`
**POST** - Mark a task as completed

**Request:**
```json
{
    "session_id": 123,
    "task_name": "Launch an EC2 instance",
    "attempts": 1
}
```

**Response:**
```json
{
    "success": true,
    "session_id": 123,
    "tasks_completed": 2,
    "tasks_total": 4,
    "progress_pct": 50
}
```

### `/api/session/progress/<session_id>`
**GET** - Get current progress for a session

**Response:**
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

### `/api/session/finalize`
**POST** - Finalize a session and calculate skill level

**Request:**
```json
{
    "session_id": 123
}
```

**Response:**
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

---

## User Flow

### Step 1: Select Learning Goal
User clicks on a learning goal card → System creates a task session

### Step 2: view Task Checklist
- Task checklist is displayed with all tasks for the goal
- Progress bar shows 0% initially
- "Complete Learning Session" button is disabled

### Step 3: Complete Tasks
- User checks off each task as they complete it
- Frontend sends request to `/api/task/complete`
- Progress bar updates in real-time
- When all tasks are completed, the button becomes enabled

### Step 4: Finalize Session
- User clicks "Complete Learning Session"
- Frontend calls `/api/session/finalize`
- System calculates:
  - Score based on completion percentage
  - Attempts from task data
  - Skill level using ML model
- Results are displayed
- User is redirected to dashboard

---

## Database Functions

### `create_tasks_for_goal(goal_key, task_list)`
Creates or updates task definitions for a goal
- Stores task list in `tasks` table
- Called when a learning session starts

### `start_task_session(user_id, goal_key, goal_title)`
Creates a new learning session
- Returns session ID
- Initializes tasks_completed to 0
- Sets tasks_total based on number of tasks

### `mark_task_completed(session_id, user_id, task_id, task_name, attempts)`
Records a task completion
- Inserts record into `task_completions`
- Updates `tasks_completed` count in `task_sessions`

### `get_task_session(session_id)`
Retrieves session details

### `get_task_completions(session_id)`
Gets all task completions for a session

### `calculate_session_metrics(session_id)`
Calculates score, attempts, and completion stats
- Returns: `{"score": X, "tasks_completed": Y, "tasks_total": Z, "attempts": A}`

### `finalize_task_session(session_id, skill_level)`
Marks session as complete and saves metrics
- Sets session_end timestamp
- Stores final_score and attempts
- Records skill_level

---

## Frontend Implementation

### Task Checklist Component (learn.html)

Key JavaScript functions:

**`completeTask(checkbox)`** - Called when checkbox changed
- Updates task styling (green border, checkmark)
- Sends `/api/task/complete` request
- Updates progress bar

**`updateProgress(completed, total)`** - Updates progress bar
- Calculates percentage
- Animates progress bar width
- Updates counter text

**`submitTasks()`** - Finalizes session
- Calls `/api/session/finalize`
- Displays result summary
- Submits old `predict` form for backward compatibility

**`resetTasks()`** - Clears all checkboxes
- Useful for restarting the session

---

## Backward Compatibility

The system maintains backward compatibility:

1. **Old Results Table** - Still stores historical results with manual input
2. **Old API Route** (`/predict`) - Still accepts manual score/time/attempts
3. **Old Billing Route** (`/billing`) - Can still manually input metrics
4. **Dashboard** - Displays all results (both old and new style)

## Migration Path

Existing users can:
1. Continue using manual input if they prefer
2. Switch to task-based learning for new goals
3. Results appear mixed on dashboard (showing improvement in task-based entries)

---

## Example: EC2 Launch Learning Path

```javascript
// User clicks EC2 goal → System creates session (ID: 123)

// Task 1: Launch an EC2 instance
// User checks checkbox → /api/task/complete
// Progress: 1/4 tasks (25%)

// Task 2: Configure security group  
// User checks checkbox → /api/task/complete
// Progress: 2/4 tasks (50%)

// Task 3: Connect to instance via SSH
// User checks checkbox → /api/task/complete
// Progress: 3/4 tasks (75%)

// Task 4: Enable CloudWatch monitoring
// User checks checkbox → /api/task/complete
// Progress: 4/4 tasks (100%)  ✓ Button enabled

// User clicks "Complete Learning Session"
// /api/session/finalize → Returns:
// {
//   "skill_level": "Intermediate",
//   "confidence": 82.5,
//   "score": 100,
//   "attempts": 2
// }

// Results saved to database
// User redirected to dashboard with new result entry
```

---

## Viva Explanation

> **Q: How does your system evaluate user performance without manual input?**
>
> **A:** We replaced manual input forms with a **task-based learning checklist**. For each learning goal (like "Launch EC2 Instance"), we define specific tasks (like "Launch instance", "Configure security group", etc.). 
>
> Users mark tasks as complete using checkboxes. The system automatically:
> - **Calculates score** = (completed tasks / total tasks) × 100
> - **Tracks time** from session start to completion
> - **Counts attempts** internally without asking users
> - **Predicts skill level** using an ML model with these calculated metrics
>
> This approach is more **realistic** (reflects actual work done), **easy to understand** (simple checklist), and **automatic** (no manual input needed).

---

## Future Enhancements

1. **Time Per Task** - Track time spent on each task individually
2. **Difficulty Weighting** - Weight tasks by difficulty for smarter scoring
3. **Task Hints** - Provide hints when user struggles with a task
4. **Auto-Progress** - Detect when tasks are completed via AWS API integration
5. **Leaderboard Integration** - Show task-based scores on leaderboard
6. **Comparison Analytics** - Compare task completion patterns across users

---

## Files Modified/Created

### Modified:
- `db.py` - Added 8 new functions for task management
- `cloud_knowledge.py` - Added TASK_DEFINITIONS and get_tasks_for_goal()
- `app.py` - Added 4 new API routes and updated /learn/start
- `templates/learn.html` - Added task checklist UI and JavaScript

### New Database Tables:
- `tasks` - Task definitions
- `task_sessions` - Learning session tracking  
- `task_completions` - Individual task completion records

---

## Testing Checklist

- [ ] Create a learning session (verify task_sessions record created)
- [ ] Mark tasks complete (verify task_completions records created)
- [ ] Check progress bar updates correctly
- [ ] Finalize session (verify score calculation correct)
- [ ] Verify results saved to database
- [ ] Confirm ML prediction works with calculated metrics
- [ ] Test all tasks completed → button enabled flow
- [ ] Test reset functionality
- [ ] Test across different browsers/devices
