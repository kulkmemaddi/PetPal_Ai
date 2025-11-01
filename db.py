import sqlite3
import json
import os
from datetime import datetime
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_path="petpal_game.db"):
        """Initialize database connection and create tables if they don't exist"""
        self.db_path = Path(db_path)
        self.connection = None
        self.connect()
        self.create_tables()
        self.initialize_default_data()
    
    def connect(self):
        """Create database connection"""
        try:
            self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
            self.connection.row_factory = sqlite3.Row  # Enable dict-like access to rows
            print(f"Connected to database: {self.db_path}")
        except sqlite3.Error as e:
            print(f"Error connecting to database: {e}")
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            print("Database connection closed")
    
    def execute_query(self, query, params=None, fetch=False):
        """Execute a database query"""
        try:
            cursor = self.connection.cursor()
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            if fetch:
                return cursor.fetchall()
            else:
                self.connection.commit()
                return cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    
    def get_user_pets(user_id):
        """Return a list of pets owned by a user"""
        db = get_database()
        pets = db.execute_query("SELECT * FROM pet WHERE user_id = ?", (user_id,), fetch=True)
        return [dict(p) for p in pets] if pets else []

    def get_pet_owner(pet_id):
        """Return the user who owns this pet"""
        db = get_database()
        pet = db.execute_query("SELECT user_id FROM pet WHERE id = ?", (pet_id,), fetch=True)
        if pet:
            user_id = pet[0]['user_id']
            user = db.execute_query("SELECT * FROM users WHERE id = ?", (user_id,), fetch=True)
            return dict(user[0]) if user else None
        return None

    
    def create_tables(self):
        """Create all database tables"""
        
        # Users table
        users_table = """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE,
            password_hash TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_login TIMESTAMP,
            is_active BOOLEAN DEFAULT 1
        )
        """
        
        # Pet table
        pet_table = """
        CREATE TABLE IF NOT EXISTS pet (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            name TEXT NOT NULL DEFAULT 'Buddy',
            species TEXT DEFAULT 'dog',
            breed TEXT DEFAULT 'mixed',
            age INTEGER DEFAULT 1,
            level INTEGER DEFAULT 1,
            experience INTEGER DEFAULT 0,
            mood TEXT DEFAULT 'happy',
            health INTEGER DEFAULT 100,
            hunger INTEGER DEFAULT 100,
            happiness INTEGER DEFAULT 100,
            energy INTEGER DEFAULT 100,
            cleanliness INTEGER DEFAULT 100,
            last_fed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_bathed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        
        # Appointments table
        appointments_table = """
        CREATE TABLE IF NOT EXISTS appointments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            appointment_type TEXT NOT NULL,
            appointment_date TIMESTAMP NOT NULL,
            veterinarian TEXT,
            clinic_name TEXT,
            notes TEXT,
            status TEXT DEFAULT 'scheduled',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pet (id)
        )
        """
        
        # Medical records table
        medical_records_table = """
        CREATE TABLE IF NOT EXISTS medical_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            record_type TEXT NOT NULL,
            diagnosis TEXT,
            treatment TEXT,
            medications TEXT,
            veterinarian TEXT,
            visit_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            follow_up_date TIMESTAMP,
            notes TEXT,
            attachments TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pet (id)
        )
        """
        
        # Reminders table
        reminders_table = """
        CREATE TABLE IF NOT EXISTS reminders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            reminder_type TEXT NOT NULL,
            due_date TIMESTAMP NOT NULL,
            repeat_interval TEXT,
            is_completed BOOLEAN DEFAULT 0,
            is_active BOOLEAN DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pet (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        
        # AI Chat History table
        ai_chathistory_table = """
        CREATE TABLE IF NOT EXISTS ai_chathistory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            user_message TEXT NOT NULL,
            ai_response TEXT NOT NULL,
            mood_context TEXT DEFAULT 'happy',
            conversation_context TEXT,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pet (id),
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        """
        
        # Achievement table
        achievement_table = """
        CREATE TABLE IF NOT EXISTS achievement (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            achievement_name TEXT NOT NULL,
            achievement_type TEXT NOT NULL,
            description TEXT,
            icon TEXT,
            points INTEGER DEFAULT 0,
            is_unlocked BOOLEAN DEFAULT 0,
            unlocked_at TIMESTAMP,
            requirement_type TEXT,
            requirement_value INTEGER,
            current_progress INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (pet_id) REFERENCES pet (id)
        )
        """
        
        # Activities table (for tracking pet activities)
        activities_table = """
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            description TEXT,
            health_effect INTEGER DEFAULT 0,
            hunger_effect INTEGER DEFAULT 0,
            happiness_effect INTEGER DEFAULT 0,
            energy_effect INTEGER DEFAULT 0,
            cleanliness_effect INTEGER DEFAULT 0,
            experience_points INTEGER DEFAULT 5,
            duration_minutes INTEGER DEFAULT 5,
            is_active BOOLEAN DEFAULT 1
        )
        """
        
        # Activity logs table
        activity_logs_table = """
        CREATE TABLE IF NOT EXISTS activity_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            activity_id INTEGER NOT NULL,
            performed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            status_before TEXT,
            status_after TEXT,
            experience_gained INTEGER DEFAULT 0,
            FOREIGN KEY (pet_id) REFERENCES pet (id),
            FOREIGN KEY (activity_id) REFERENCES activities (id)
        )
        """
        
        # Scenes table
        scenes_table = """
        CREATE TABLE IF NOT EXISTS scenes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            display_name TEXT NOT NULL,
            image_path TEXT,
            mood_requirement TEXT,
            is_active BOOLEAN DEFAULT 1,
            unlock_level INTEGER DEFAULT 1
        )
        """
        
        # Execute table creation
        tables = [
            users_table, pet_table, appointments_table, medical_records_table,
            reminders_table, ai_chathistory_table, achievement_table,
            activities_table, activity_logs_table, scenes_table
        ]
        
        for table in tables:
            self.execute_query(table)
        
        print("All database tables created successfully")
    
    def initialize_default_data(self):
        """Initialize database with default data"""
        
        # Check if default user exists
        user = self.execute_query("SELECT id FROM users WHERE username = ?", ('default_user',), fetch=True)
        if not user:
            # Create default user
            user_id = self.execute_query(
                "INSERT INTO users (username, email, is_active) VALUES (?, ?, ?)",
                ('default_user', 'user@petpal.com', 1)
            )
            print("Created default user")
        else:
            user_id = user[0]['id']
        
        # Check if default pet exists
        pet = self.execute_query("SELECT id FROM pet WHERE user_id = ?", (user_id,), fetch=True)
        if not pet:
            # Create default pet
            pet_id = self.execute_query(
                """INSERT INTO pet (user_id, name, species, breed, mood, health, hunger, 
                   happiness, energy, cleanliness) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (user_id, 'Buddy', 'dog', 'Golden Retriever', 'happy', 100, 80, 90, 100, 100)
            )
            print("Created default pet")
        else:
            pet_id = pet[0]['id']
        
        # Initialize default activities
        default_activities = [
            ('Feed Pet', 'Give your pet some delicious food', 5, 20, 10, -5, 0, 10),
            ('Play with Pet', 'Play games and have fun together', 10, -10, 25, -15, -5, 15),
            ('Pet Bath', 'Give your pet a nice warm bath', 5, 0, 10, -5, 30, 8),
            ('Vet Visit', 'Take your pet for a health checkup', 30, 0, -5, -10, 5, 20),
            ('Nap Time', 'Let your pet rest and recharge', 5, 0, 10, 30, 0, 5),
            ('Training', 'Teach your pet new tricks', 10, -5, 15, -10, 0, 25),
            ('Grooming', 'Professional grooming session', 8, 0, 15, -8, 25, 12),
            ('Walk', 'Take a nice walk around the neighborhood', 15, -8, 20, -12, -3, 18)
        ]
        
        for activity in default_activities:
            existing = self.execute_query("SELECT id FROM activities WHERE name = ?", (activity[0],), fetch=True)
            if not existing:
                self.execute_query(
                    """INSERT INTO activities (name, description, health_effect, hunger_effect, 
                       happiness_effect, energy_effect, cleanliness_effect, experience_points) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    activity
                )
        
        # Initialize default scenes
        default_scenes = [
            ('normal_home', 'Home', 'assets/backgrounds/normal_home.png', '', 1),
            ('feeding', 'Kitchen', 'assets/backgrounds/feeding.png', 'eating', 1),
            ('sleeping', 'Bedroom', 'assets/backgrounds/sleeping.png', 'sleeping', 1),
            ('showering', 'Bathroom', 'assets/backgrounds/showering.png', 'showering', 1),
            ('play', 'Playground', 'assets/backgrounds/play.png', 'playing', 1),
            ('sick', 'Vet Clinic', 'assets/backgrounds/sick.png', 'sick', 1),
            ('park', 'Dog Park', 'assets/backgrounds/park.png', 'playing', 5),
            ('beach', 'Beach', 'assets/backgrounds/beach.png', 'happy', 10)
        ]
        
        for scene in default_scenes:
            existing = self.execute_query("SELECT id FROM scenes WHERE name = ?", (scene[0],), fetch=True)
            if not existing:
                self.execute_query(
                    """INSERT INTO scenes (name, display_name, image_path, mood_requirement, unlock_level) 
                       VALUES (?, ?, ?, ?, ?)""",
                    scene
                )
        
        # Initialize default achievements
        default_achievements = [
            ('First Steps', 'welcome', 'Welcome to PetPal!', 'star', 10, 'days_alive', 1),
            ('Best Friend', 'friendship', 'Reach 100 happiness', 'heart', 50, 'happiness', 100),
            ('Healthy Pet', 'health', 'Maintain 90+ health for 7 days', 'plus', 75, 'health_streak', 7),
            ('Clean Freak', 'cleanliness', 'Keep pet clean for 5 days', 'droplets', 25, 'clean_streak', 5),
            ('Player', 'activity', 'Play 50 times', 'game-controller', 100, 'play_count', 50),
            ('Chef', 'feeding', 'Feed pet 100 times', 'chef-hat', 75, 'feed_count', 100),
            ('Veteran', 'experience', 'Reach level 10', 'trophy', 200, 'level', 10)
        ]
        
        for achievement in default_achievements:
            existing = self.execute_query(
                "SELECT id FROM achievement WHERE pet_id = ? AND achievement_name = ?", 
                (pet_id, achievement[0]), fetch=True
            )
            if not existing:
                self.execute_query(
                    """INSERT INTO achievement (pet_id, achievement_name, achievement_type, 
                       description, icon, points, requirement_type, requirement_value) 
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                    (pet_id, achievement[0], achievement[1], achievement[2], 
                     achievement[3], achievement[4], achievement[5], achievement[6])
                )
        
        print("Default data initialized")


# Database operation functions
db = None

def init_database(db_path="petpal_game.db"):
    """Initialize the database connection"""
    global db
    db = DatabaseManager(db_path)
    return db

def get_database():
    """Get the database instance"""
    global db
    if db is None:
        db = init_database()
    return db

# Pet-related functions
def get_or_create_pet(user_id=1):
    """Get or create a pet for the user"""
    database = get_database()
    
    # Try to get existing pet
    pet = database.execute_query(
        "SELECT * FROM pet WHERE user_id = ? LIMIT 1", 
        (user_id,), fetch=True
    )
    
    if pet:
        return dict(pet[0])  # Convert sqlite3.Row to dict
    
    # Create new pet if none exists
    pet_id = database.execute_query(
        """INSERT INTO pet (user_id, name, species, breed, mood, health, hunger, 
           happiness, energy, cleanliness) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (user_id, 'Buddy', 'dog', 'Golden Retriever', 'happy', 100, 80, 90, 100, 100)
    )
    
    # Return the newly created pet
    pet = database.execute_query(
        "SELECT * FROM pet WHERE id = ?", 
        (pet_id,), fetch=True
    )
    
    return dict(pet[0])

def update_pet_status(pet_id=None, **kwargs):
    """Update pet status"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    # Build update query dynamically
    valid_fields = ['mood', 'health', 'hunger', 'happiness', 'energy', 'cleanliness', 
                   'last_fed', 'last_played', 'last_bathed', 'experience', 'level']
    
    updates = []
    values = []
    
    for field, value in kwargs.items():
        if field in valid_fields:
            if field in ['health', 'hunger', 'happiness', 'energy', 'cleanliness']:
                # Clamp values between 0 and 100
                value = max(0, min(100, value))
            updates.append(f"{field} = ?")
            values.append(value)
    
    if updates:
        updates.append("updated_at = CURRENT_TIMESTAMP")
        query = f"UPDATE pet SET {', '.join(updates)} WHERE id = ?"
        values.append(pet_id)
        
        database.execute_query(query, values)
    
    # Return updated pet
    pet = database.execute_query("SELECT * FROM pet WHERE id = ?", (pet_id,), fetch=True)
    return dict(pet[0]) if pet else None

def perform_activity(activity_name, pet_id=None):
    """Perform an activity and update pet status"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    # Get activity details
    activity = database.execute_query(
        "SELECT * FROM activities WHERE name = ?", 
        (activity_name,), fetch=True
    )
    
    if not activity:
        print(f"Activity '{activity_name}' not found")
        return None
    
    activity = dict(activity[0])
    
    # Get current pet status
    pet = database.execute_query("SELECT * FROM pet WHERE id = ?", (pet_id,), fetch=True)
    if not pet:
        print(f"Pet with id {pet_id} not found")
        return None
    
    pet = dict(pet[0])
    
    # Store status before activity
    status_before = {
        'health': pet['health'],
        'hunger': pet['hunger'],
        'happiness': pet['happiness'],
        'energy': pet['energy'],
        'cleanliness': pet['cleanliness'],
        'experience': pet['experience']
    }
    
    # Calculate new values
    new_health = max(0, min(100, pet['health'] + activity['health_effect']))
    new_hunger = max(0, min(100, pet['hunger'] + activity['hunger_effect']))
    new_happiness = max(0, min(100, pet['happiness'] + activity['happiness_effect']))
    new_energy = max(0, min(100, pet['energy'] + activity['energy_effect']))
    new_cleanliness = max(0, min(100, pet['cleanliness'] + activity['cleanliness_effect']))
    new_experience = pet['experience'] + activity['experience_points']
    
    # Check for level up
    new_level = pet['level']
    experience_needed = new_level * 100  # Simple level calculation
    if new_experience >= experience_needed:
        new_level += 1
    
    # Update pet
    updated_pet = update_pet_status(
        pet_id=pet_id,
        health=new_health,
        hunger=new_hunger,
        happiness=new_happiness,
        energy=new_energy,
        cleanliness=new_cleanliness,
        experience=new_experience,
        level=new_level
    )
    
    # Store status after activity
    status_after = {
        'health': new_health,
        'hunger': new_hunger,
        'happiness': new_happiness,
        'energy': new_energy,
        'cleanliness': new_cleanliness,
        'experience': new_experience
    }
    
    # Log the activity
    database.execute_query(
        """INSERT INTO activity_logs (pet_id, activity_id, status_before, status_after, experience_gained) 
           VALUES (?, ?, ?, ?, ?)""",
        (pet_id, activity['id'], json.dumps(status_before), 
         json.dumps(status_after), activity['experience_points'])
    )
    
    # Check and unlock achievements
    check_achievements(pet_id)
    
    return updated_pet

# Chat functions
def save_chat_message(user_message, ai_response, pet_id=None, user_id=1):
    """Save chat conversation to database"""
    if pet_id is None:
        pet = get_or_create_pet(user_id)
        pet_id = pet['id']
    
    database = get_database()
    
    # Get current pet mood for context
    pet = database.execute_query("SELECT mood FROM pet WHERE id = ?", (pet_id,), fetch=True)
    mood_context = pet[0]['mood'] if pet else 'happy'
    
    chat_id = database.execute_query(
        """INSERT INTO ai_chathistory (pet_id, user_id, user_message, ai_response, mood_context) 
           VALUES (?, ?, ?, ?, ?)""",
        (pet_id, user_id, user_message, ai_response, mood_context)
    )
    
    return chat_id

def get_recent_chats(pet_id=None, user_id=1, limit=10):
    """Get recent chat history"""
    if pet_id is None:
        pet = get_or_create_pet(user_id)
        pet_id = pet['id']
    
    database = get_database()
    
    chats = database.execute_query(
        """SELECT * FROM ai_chathistory WHERE pet_id = ? 
           ORDER BY timestamp DESC LIMIT ?""",
        (pet_id, limit), fetch=True
    )
    
    return [dict(chat) for chat in chats] if chats else []

# Scene functions
def get_current_scene(pet_id=None):
    """Get appropriate scene based on pet mood and level"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    # Get pet info
    pet = database.execute_query("SELECT mood, level FROM pet WHERE id = ?", (pet_id,), fetch=True)
    if not pet:
        return None
    
    pet = dict(pet[0])
    
    # Try to get scene matching current mood and level
    scene = database.execute_query(
        """SELECT * FROM scenes WHERE mood_requirement = ? AND unlock_level <= ? AND is_active = 1 
           ORDER BY unlock_level DESC LIMIT 1""",
        (pet['mood'], pet['level']), fetch=True
    )
    
    if scene:
        return dict(scene[0])
    
    # Fall back to default home scene
    scene = database.execute_query(
        "SELECT * FROM scenes WHERE name = 'normal_home' AND is_active = 1 LIMIT 1", 
        fetch=True
    )
    
    return dict(scene[0]) if scene else None

def get_available_scenes(pet_level=1):
    """Get all available scenes for pet level"""
    database = get_database()
    
    scenes = database.execute_query(
        "SELECT * FROM scenes WHERE unlock_level <= ? AND is_active = 1 ORDER BY unlock_level",
        (pet_level,), fetch=True
    )
    
    return [dict(scene) for scene in scenes] if scenes else []

# Achievement functions
def check_achievements(pet_id=None):
    """Check and unlock achievements"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    # Get pet stats
    pet = database.execute_query("SELECT * FROM pet WHERE id = ?", (pet_id,), fetch=True)
    if not pet:
        return
    
    pet = dict(pet[0])
    
    # Get unlockable achievements
    achievements = database.execute_query(
        "SELECT * FROM achievement WHERE pet_id = ? AND is_unlocked = 0",
        (pet_id,), fetch=True
    )
    
    newly_unlocked = []
    
    for achievement in achievements:
        achievement = dict(achievement)
        requirement_type = achievement['requirement_type']
        requirement_value = achievement['requirement_value']
        should_unlock = False
        
        if requirement_type == 'level':
            should_unlock = pet['level'] >= requirement_value
        elif requirement_type == 'happiness':
            should_unlock = pet['happiness'] >= requirement_value
        elif requirement_type == 'health':
            should_unlock = pet['health'] >= requirement_value
        elif requirement_type == 'days_alive':
            # Calculate days since creation
            created_at = datetime.fromisoformat(pet['created_at'].replace('Z', '+00:00'))
            days_alive = (datetime.now() - created_at).days
            should_unlock = days_alive >= requirement_value
        elif requirement_type in ['play_count', 'feed_count']:
            # Count activities
            activity_name = 'Play with Pet' if requirement_type == 'play_count' else 'Feed Pet'
            activity = database.execute_query(
                "SELECT id FROM activities WHERE name = ?", (activity_name,), fetch=True
            )
            if activity:
                count = database.execute_query(
                    "SELECT COUNT(*) as count FROM activity_logs WHERE pet_id = ? AND activity_id = ?",
                    (pet_id, activity[0]['id']), fetch=True
                )
                should_unlock = count[0]['count'] >= requirement_value if count else False
        
        if should_unlock:
            # Unlock achievement
            database.execute_query(
                "UPDATE achievement SET is_unlocked = 1, unlocked_at = CURRENT_TIMESTAMP WHERE id = ?",
                (achievement['id'],)
            )
            newly_unlocked.append(achievement)
    
    return newly_unlocked

def get_pet_achievements(pet_id=None, unlocked_only=False):
    """Get pet achievements"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    query = "SELECT * FROM achievement WHERE pet_id = ?"
    params = [pet_id]
    
    if unlocked_only:
        query += " AND is_unlocked = 1"
    
    query += " ORDER BY unlocked_at DESC, achievement_name"
    
    achievements = database.execute_query(query, params, fetch=True)
    return [dict(achievement) for achievement in achievements] if achievements else []

# Appointment functions
def add_appointment(pet_id, appointment_type, appointment_date, veterinarian=None, clinic_name=None, notes=None):
    """Add a new appointment"""
    database = get_database()
    
    appointment_id = database.execute_query(
        """INSERT INTO appointments (pet_id, appointment_type, appointment_date, 
           veterinarian, clinic_name, notes) VALUES (?, ?, ?, ?, ?, ?)""",
        (pet_id, appointment_type, appointment_date, veterinarian, clinic_name, notes)
    )
    
    return appointment_id

def get_upcoming_appointments(pet_id=None, days_ahead=30):
    """Get upcoming appointments"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    from datetime import datetime, timedelta
    future_date = datetime.now() + timedelta(days=days_ahead)
    
    appointments = database.execute_query(
        """SELECT * FROM appointments WHERE pet_id = ? AND appointment_date > datetime('now') 
           AND appointment_date <= ? AND status != 'cancelled' ORDER BY appointment_date""",
        (pet_id, future_date.isoformat()), fetch=True
    )
    
    return [dict(appointment) for appointment in appointments] if appointments else []

# Medical records functions
def add_medical_record(pet_id, record_type, diagnosis=None, treatment=None, medications=None, 
                      veterinarian=None, visit_date=None, notes=None):
    """Add a new medical record"""
    database = get_database()
    
    if visit_date is None:
        visit_date = datetime.now().isoformat()
    
    record_id = database.execute_query(
        """INSERT INTO medical_records (pet_id, record_type, diagnosis, treatment, 
           medications, veterinarian, visit_date, notes) 
           VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (pet_id, record_type, diagnosis, treatment, medications, veterinarian, visit_date, notes)
    )
    
    return record_id

def get_medical_history(pet_id=None, limit=20):
    """Get pet medical history"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    records = database.execute_query(
        "SELECT * FROM medical_records WHERE pet_id = ? ORDER BY visit_date DESC LIMIT ?",
        (pet_id, limit), fetch=True
    )
    
    return [dict(record) for record in records] if records else []

# Reminder functions
def add_reminder(pet_id, user_id, title, description, due_date, reminder_type, repeat_interval=None):
    """Add a new reminder"""
    database = get_database()
    
    reminder_id = database.execute_query(
        """INSERT INTO reminders (pet_id, user_id, title, description, due_date, 
           reminder_type, repeat_interval) VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (pet_id, user_id, title, description, due_date, reminder_type, repeat_interval)
    )
    
    return reminder_id

def get_active_reminders(pet_id=None, user_id=1):
    """Get active reminders"""
    if pet_id is None:
        pet = get_or_create_pet()
        pet_id = pet['id']
    
    database = get_database()
    
    reminders = database.execute_query(
        """SELECT * FROM reminders WHERE pet_id = ? AND user_id = ? 
           AND is_active = 1 AND is_completed = 0 ORDER BY due_date""",
        (pet_id, user_id), fetch=True
    )
    
    return [dict(reminder) for reminder in reminders] if reminders else []

# Utility functions
def close_database():
    """Close database connection"""
    global db
    if db:
        db.close()
        db = None

def reset_database():
    """Reset database (delete and recreate)"""
    global db
    if db:
        db.close()
    
    # Delete database file
    try:
        os.remove("petpal_game.db")
        print("Database file deleted")
    except FileNotFoundError:
        pass
    
    # Reinitialize
    db = init_database()
    print("Database reset complete")

# Command line interface
if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'init':
            print("Initializing database...")
            init_database()
            print("Database initialization complete")
        elif sys.argv[1] == 'reset':
            print("Resetting database...")
            reset_database()
            print("Database reset complete")
        elif sys.argv[1] == 'test':
            print("Testing database operations...")
            
            # Initialize database
            init_database()
            
            # Test pet operations
            print("\n--- Testing Pet Operations ---")
            pet = get_or_create_pet()
            print(f"Pet created: {pet['name']} (ID: {pet['id']})")
            
            # Test activity
            print("\n--- Testing Activity ---")
            result = perform_activity("Feed Pet", pet['id'])
            if result:
                print(f"Activity completed. New hunger: {result['hunger']}")
            
            # Test chat
            print("\n--- Testing Chat ---")
            chat_id = save_chat_message("Hello!", "Woof! Hello there!", pet['id'])
            print(f"Chat saved with ID: {chat_id}")
            
            recent_chats = get_recent_chats(pet['id'])
            print(f"Recent chats: {len(recent_chats)} found")
            
            # Test achievements
            print("\n--- Testing Achievements ---")
            achievements = get_pet_achievements(pet['id'])
            print(f"Total achievements: {len(achievements)}")
            unlocked = [a for a in achievements if a['is_unlocked']]
            print(f"Unlocked achievements: {len(unlocked)}")
            
            # Test appointments
            print("\n--- Testing Appointments ---")
            from datetime import datetime, timedelta
            future_date = datetime.now() + timedelta(days=7)
            appointment_id = add_appointment(
                pet['id'], 'checkup', future_date.isoformat(), 
                'Dr. Smith', 'Pet Care Clinic', 'Regular checkup'
            )
            print(f"Appointment created with ID: {appointment_id}")
            
            upcoming = get_upcoming_appointments(pet['id'])
            print(f"Upcoming appointments: {len(upcoming)}")
            
            # Test medical records
            print("\n--- Testing Medical Records ---")
            record_id = add_medical_record(
                pet['id'], 'vaccination', 'Healthy', 'Rabies vaccination', 
                'Rabies vaccine', 'Dr. Smith', None, 'Annual vaccination'
            )
            print(f"Medical record created with ID: {record_id}")
            
            history = get_medical_history(pet['id'])
            print(f"Medical records: {len(history)}")
            
            # Test reminders
            print("\n--- Testing Reminders ---")
            reminder_date = datetime.now() + timedelta(days=30)
            reminder_id = add_reminder(
                pet['id'], 1, 'Annual Checkup', 'Time for annual vet checkup',
                reminder_date.isoformat(), 'vet', 'yearly'
            )
            print(f"Reminder created with ID: {reminder_id}")
            
            active_reminders = get_active_reminders(pet['id'])
            print(f"Active reminders: {len(active_reminders)}")
            
            print("\n--- Database Test Complete ---")
            
        else:
            print("Usage: python db.py [init|reset|test]")
    else:
        print("Database module loaded.")
        print("Commands:")
        print("  python db.py init  - Initialize database")
        print("  python db.py reset - Reset database")
        print("  python db.py test  - Test database operations")