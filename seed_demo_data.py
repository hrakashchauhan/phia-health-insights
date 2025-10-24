import sqlite3
import hashlib
from datetime import datetime, timedelta
import random

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def seed_demo_data():
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    
    # Create demo user
    try:
        c.execute("INSERT INTO users (username, password, email, created_at, subscription) VALUES (?, ?, ?, ?, ?)",
                 ('demo_user', hash_password('demo123'), 'demo@phia.com', datetime.now().isoformat(), 'premium'))
        user_id = c.lastrowid
        
        # Create sample health data for last 14 days
        for i in range(14):
            date = (datetime.now() - timedelta(days=i)).date().isoformat()
            sleep = round(random.uniform(6.5, 8.5), 1)
            steps = random.randint(6000, 12000)
            hr = random.randint(58, 75)
            stress = random.randint(65, 90)
            weight = round(random.uniform(68, 72), 1)
            mood = random.randint(6, 9)
            
            c.execute("""INSERT INTO health_data 
                         (user_id, date, sleep_hours, steps, heart_rate, stress_score, weight, mood)
                         VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (user_id, date, sleep, steps, hr, stress, weight, mood))
        
        # Create sample goals
        c.execute("INSERT INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
                 (user_id, 'Daily Steps', 10000, 8500, (datetime.now() + timedelta(days=30)).date().isoformat()))
        c.execute("INSERT INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
                 (user_id, 'Sleep Hours', 8.0, 7.2, (datetime.now() + timedelta(days=30)).date().isoformat()))
        
        conn.commit()
        print("✅ Demo data seeded successfully!")
        
    except sqlite3.IntegrityError:
        print("ℹ️ Demo user already exists")
    
    conn.close()

if __name__ == "__main__":
    seed_demo_data()
