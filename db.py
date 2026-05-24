import sqlite3
import hashlib
import os

DB_PATH = "database.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT DEFAULT 'user',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            score INTEGER NOT NULL,
            time_taken INTEGER NOT NULL,
            attempts INTEGER NOT NULL,
            skill_level TEXT NOT NULL,
            difficulty TEXT NOT NULL,
            cpu TEXT NOT NULL,
            ram TEXT NOT NULL,
            gpu TEXT NOT NULL,
            cost REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Ensure 'notes' column exists in case the table was already created
    try:
        c.execute("ALTER TABLE results ADD COLUMN notes TEXT")
    except sqlite3.OperationalError:
        pass

    # Learning sessions table for Cloud Learning Path Recommender
    c.execute('''
        CREATE TABLE IF NOT EXISTS learning_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            goal_key TEXT NOT NULL,
            goal_title TEXT NOT NULL,
            skill_level TEXT NOT NULL,
            instance_type TEXT NOT NULL,
            cpu TEXT NOT NULL,
            ram TEXT NOT NULL,
            gpu TEXT NOT NULL,
            cost REAL NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Billing records table for Smart Billing Engine
    c.execute('''
        CREATE TABLE IF NOT EXISTS billing_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            username TEXT NOT NULL,
            goal_key TEXT NOT NULL,
            goal_title TEXT NOT NULL,
            base_cost REAL NOT NULL,
            efficiency_level TEXT NOT NULL,
            efficiency_score REAL NOT NULL,
            final_cost REAL NOT NULL,
            savings REAL NOT NULL,
            savings_pct INTEGER NOT NULL,
            resources_summary TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    ''')

    # Task definitions table
    c.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            goal_key TEXT NOT NULL,
            task_name TEXT NOT NULL,
            task_description TEXT,
            task_order INTEGER NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(goal_key, task_name)
        )
    ''')

    # Task learning sessions table - tracks each learning session with task progress
    c.execute('''
        CREATE TABLE IF NOT EXISTS task_sessions (
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
    ''')

    # Task completions table - tracks individual task completions
    c.execute('''
        CREATE TABLE IF NOT EXISTS task_completions (
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
    ''')

    # Create default admin account
    admin_pass = hashlib.sha256("admin123".encode()).hexdigest()
    c.execute("INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
              ("admin", admin_pass, "admin"))

    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password):
    conn = get_db()
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                  (username, hash_password(password)))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def get_user(username, password):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=? AND password=?",
              (username, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def save_result(user_id, username, score, time_taken, attempts, skill_level,
                difficulty, cpu, ram, gpu, cost, notes=""):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO results
        (user_id, username, score, time_taken, attempts, skill_level,
         difficulty, cpu, ram, gpu, cost, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, score, time_taken, attempts, skill_level,
          difficulty, cpu, ram, gpu, cost, notes))
    conn.commit()
    conn.close()

def get_all_results():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM results ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_user_results(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM results WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def get_leaderboard():
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT username,
               COUNT(*) as total_sessions,
               AVG(score) as avg_score,
               MAX(score) as best_score,
               SUM(cost) as total_cost
        FROM results
        GROUP BY username
        ORDER BY avg_score DESC
        LIMIT 20
    ''')
    rows = c.fetchall()
    conn.close()
    return rows

def get_all_users():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT id, username, role, created_at FROM users ORDER BY created_at DESC")
    rows = c.fetchall()
    conn.close()
    return rows

def get_stats():
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT COUNT(*) FROM users")
    total_users = c.fetchone()[0]
    c.execute("SELECT COUNT(*) FROM results")
    total_sessions = c.fetchone()[0]
    c.execute("SELECT AVG(score) FROM results")
    avg_score = c.fetchone()[0] or 0
    c.execute("SELECT SUM(cost) FROM results")
    total_cost = c.fetchone()[0] or 0
    c.execute("SELECT skill_level, COUNT(*) FROM results GROUP BY skill_level")
    skill_dist = dict(c.fetchall())
    conn.close()
    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "avg_score": round(avg_score, 1),
        "total_cost": round(total_cost, 2),
        "skill_dist": skill_dist
    }

def update_password(user_id, password):
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE users SET password=? WHERE id=?", (hash_password(password), user_id))
    conn.commit()
    conn.close()
    return True

def delete_user_cascade(user_id):
    conn = get_db()
    c = conn.cursor()
    # Delete from results first
    c.execute("DELETE FROM results WHERE user_id=?", (user_id,))
    # Delete from users
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return True

def save_learning_session(user_id, username, goal_key, goal_title, skill_level,
                          instance_type, cpu, ram, gpu, cost):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO learning_sessions
        (user_id, username, goal_key, goal_title, skill_level,
         instance_type, cpu, ram, gpu, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, goal_key, goal_title, skill_level,
          instance_type, cpu, ram, gpu, cost))
    conn.commit()
    conn.close()

def get_user_learning_sessions(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM learning_sessions WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def save_billing_record(user_id, username, goal_key, goal_title,
                        base_cost, efficiency_level, efficiency_score,
                        final_cost, savings, savings_pct, resources_summary):
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO billing_records
        (user_id, username, goal_key, goal_title, base_cost,
         efficiency_level, efficiency_score, final_cost, savings,
         savings_pct, resources_summary)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, username, goal_key, goal_title, base_cost,
          efficiency_level, efficiency_score, final_cost, savings,
          savings_pct, resources_summary))
    conn.commit()
    conn.close()

def get_user_billing(user_id):
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM billing_records WHERE user_id=? ORDER BY created_at DESC", (user_id,))
    rows = c.fetchall()
    conn.close()
    return rows

# ─── Task Management ─────────────────────────────────────────────────────────

def create_tasks_for_goal(goal_key, task_list):
    """Create or update tasks for a learning goal."""
    conn = get_db()
    c = conn.cursor()
    try:
        for idx, task_name in enumerate(task_list, 1):
            c.execute('''
                INSERT OR IGNORE INTO tasks
                (goal_key, task_name, task_order)
                VALUES (?, ?, ?)
            ''', (goal_key, task_name, idx))
        conn.commit()
        return True
    except Exception as e:
        print(f"Error creating tasks: {e}")
        return False
    finally:
        conn.close()

def get_tasks_for_goal(goal_key):
    """Get task definitions for a learning goal (stored in DB or fallback to definitions)."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT id, goal_key, task_name, task_description, task_order
        FROM tasks
        WHERE goal_key = ?
        ORDER BY task_order ASC
    ''', (goal_key,))
    rows = c.fetchall()
    conn.close()
    # If no tasks found in DB, could fallback to definitions, but we'll create them first
    return rows

def start_task_session(user_id, goal_key, goal_title):
    """Create a new task learning session."""
    conn = get_db()
    c = conn.cursor()
    
    # Get total tasks for this goal
    c.execute("SELECT COUNT(*) FROM tasks WHERE goal_key = ?", (goal_key,))
    tasks_total = c.fetchone()[0]
    
    c.execute('''
        INSERT INTO task_sessions
        (user_id, goal_key, goal_title, tasks_total)
        VALUES (?, ?, ?, ?)
    ''', (user_id, goal_key, goal_title, tasks_total))
    
    session_id = c.lastrowid
    conn.commit()
    conn.close()
    return session_id

def mark_task_completed(task_session_id, user_id, task_id, task_name, attempts=1):
    """Mark a task as completed in a session."""
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''
        INSERT INTO task_completions
        (task_session_id, user_id, task_id, task_name, attempts_before_completion)
        VALUES (?, ?, ?, ?, ?)
    ''', (task_session_id, user_id, task_id, task_name, attempts))
    
    # Update the task session to increment completed tasks
    c.execute('''
        UPDATE task_sessions
        SET tasks_completed = (
            SELECT COUNT(*) FROM task_completions WHERE task_session_id = ?
        )
        WHERE id = ?
    ''', (task_session_id, task_session_id))
    
    conn.commit()
    conn.close()

def get_task_session(session_id):
    """Get a specific task session."""
    conn = get_db()
    c = conn.cursor()
    c.execute("SELECT * FROM task_sessions WHERE id = ?", (session_id,))
    row = c.fetchone()
    conn.close()
    return row

def get_task_completions(session_id):
    """Get all task completions for a session."""
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        SELECT * FROM task_completions
        WHERE task_session_id = ?
        ORDER BY completed_at ASC
    ''', (session_id,))
    rows = c.fetchall()
    conn.close()
    return rows

def calculate_session_metrics(session_id):
    """Calculate score, time, and attempts from task completions."""
    conn = get_db()
    c = conn.cursor()
    
    # Get session info
    c.execute("SELECT * FROM task_sessions WHERE id = ?", (session_id,))
    session = c.fetchone()
    
    if not session:
        conn.close()
        return None
    
    # Calculate score: (completed tasks / total tasks) * 100
    tasks_completed = session["tasks_completed"]
    tasks_total = session["tasks_total"] or 1
    score = int((tasks_completed / tasks_total) * 100)
    
    # Get time range from first to last completion
    c.execute('''
        SELECT MIN(completed_at) as start_time, MAX(completed_at) as end_time
        FROM task_completions
        WHERE task_session_id = ?
    ''', (session_id,))
    times = c.fetchone()
    
    # Calculate attempts (sum of attempts across all tasks, or count of completions)
    c.execute('''
        SELECT SUM(attempts_before_completion)
        FROM task_completions
        WHERE task_session_id = ?
    ''', (session_id,))
    attempts = c.fetchone()[0] or tasks_completed
    
    conn.close()
    
    return {
        "score": score,
        "tasks_completed": tasks_completed,
        "tasks_total": tasks_total,
        "attempts": attempts
    }

def finalize_task_session(session_id, skill_level):
    """Mark task session as complete and save metrics."""
    conn = get_db()
    c = conn.cursor()
    
    metrics = calculate_session_metrics(session_id)
    if not metrics:
        conn.close()
        return False
    
    c.execute('''
        UPDATE task_sessions
        SET session_end = CURRENT_TIMESTAMP,
            final_score = ?,
            attempts = ?,
            skill_level = ?
        WHERE id = ?
    ''', (metrics["score"], metrics["attempts"], skill_level, session_id))
    
    c.execute('''
        UPDATE results
        SET score = ?, attempts = ?
        WHERE id = (
            SELECT id FROM results 
            WHERE user_id = (SELECT user_id FROM task_sessions WHERE id = ?)
            ORDER BY created_at DESC LIMIT 1
        )
    ''', (metrics["score"], metrics["attempts"], session_id))
    
    conn.commit()
    conn.close()
    return True
