import sqlite3

# Connect to both databases
main_conn = sqlite3.connect("petpal_game.db")
secondary_conn = sqlite3.connect("appointments_medical.db")

main_cursor = main_conn.cursor()
secondary_cursor = secondary_conn.cursor()

# --- Ensure tables exist in main DB (create if needed)
main_cursor.execute("""
CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pet_id INTEGER,
    appointment_type TEXT,
    date TEXT,
    notes TEXT
)
""")

main_cursor.execute("""
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
""")

# --- Copy data over
secondary_cursor.execute("SELECT * FROM appointments")
appointments = secondary_cursor.fetchall()

secondary_cursor.execute("SELECT * FROM medical_records")
medical = secondary_cursor.fetchall()

# Insert into main DB
if appointments:
    main_cursor.executemany("INSERT INTO appointments VALUES (?, ?, ?, ?, ?)", appointments)

if medical:
    main_cursor.executemany("""
        INSERT INTO medical_records 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, medical)

main_conn.commit()
print("✅ Data merged successfully!")

main_conn.close()
secondary_conn.close()
