import sqlite3
import hashlib
from datetime import datetime, timedelta
import random
import numpy as np

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_enhanced_demo_data():
    conn = sqlite3.connect('phia_mvp.db')
    c = conn.cursor()
    
    # Create multiple demo users with different health profiles
    demo_users = [
        ('demo_user', 'demo123', 'demo@phia.com', 'premium', 'Active Professional'),
        ('health_enthusiast', 'health123', 'enthusiast@phia.com', 'premium', 'Fitness Focused'),
        ('wellness_seeker', 'wellness123', 'wellness@phia.com', 'premium', 'Wellness Journey'),
        ('busy_parent', 'parent123', 'parent@phia.com', 'premium', 'Work-Life Balance')
    ]
    
    for username, password, email, subscription, profile_type in demo_users:
        try:
            c.execute("INSERT INTO users (username, password, email, created_at, subscription) VALUES (?, ?, ?, ?, ?)",
                     (username, hash_password(password), email, datetime.now().isoformat(), subscription))
            user_id = c.lastrowid
            
            # Create 30 days of realistic health data
            for i in range(30):
                date = (datetime.now() - timedelta(days=i)).date().isoformat()
                
                # Generate realistic data based on profile
                if profile_type == 'Active Professional':
                    sleep = np.random.normal(7.2, 0.6, 1)[0]
                    steps = int(np.random.normal(9500, 1200, 1)[0])
                    hr = int(np.random.normal(62, 4, 1)[0])
                    stress = int(np.random.normal(75, 8, 1)[0])
                elif profile_type == 'Fitness Focused':
                    sleep = np.random.normal(8.0, 0.4, 1)[0]
                    steps = int(np.random.normal(12000, 1500, 1)[0])
                    hr = int(np.random.normal(58, 3, 1)[0])
                    stress = int(np.random.normal(82, 6, 1)[0])
                elif profile_type == 'Wellness Journey':
                    sleep = np.random.normal(7.8, 0.5, 1)[0]
                    steps = int(np.random.normal(8500, 1000, 1)[0])
                    hr = int(np.random.normal(65, 5, 1)[0])
                    stress = int(np.random.normal(78, 10, 1)[0])
                else:  # Busy Parent
                    sleep = np.random.normal(6.8, 0.8, 1)[0]
                    steps = int(np.random.normal(7500, 1500, 1)[0])
                    hr = int(np.random.normal(68, 6, 1)[0])
                    stress = int(np.random.normal(68, 12, 1)[0])
                
                # Ensure realistic ranges
                sleep = max(5.0, min(10.0, sleep))
                steps = max(2000, min(20000, steps))
                hr = max(50, min(90, hr))
                stress = max(30, min(100, stress))
                weight = round(random.uniform(65, 75), 1)
                mood = random.randint(6, 9)
                
                c.execute("""INSERT OR REPLACE INTO health_data 
                             (user_id, date, sleep_hours, steps, heart_rate, stress_score, weight, mood)
                             VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                         (user_id, date, sleep, steps, hr, stress, weight, mood))
            
            # Create realistic goals
            goals_data = [
                ('Daily Steps', 10000, 'Reach 10,000 steps daily'),
                ('Sleep Hours', 8.0, 'Get 8 hours of quality sleep'),
                ('Stress Management', 85, 'Maintain stress score above 85'),
                ('Weight Management', 70.0, 'Maintain healthy weight')
            ]
            
            for goal_type, target, description in goals_data:
                deadline = (datetime.now() + timedelta(days=random.randint(30, 90))).date().isoformat()
                c.execute("INSERT OR REPLACE INTO goals (user_id, goal_type, target_value, current_value, deadline) VALUES (?, ?, ?, ?, ?)",
                         (user_id, goal_type, target, 0, deadline))
            
        except sqlite3.IntegrityError:
            pass  # User already exists
    
    conn.commit()
    conn.close()
    print("✅ Enhanced demo data created for all user profiles!")

if __name__ == "__main__":
    create_enhanced_demo_data()
