import sqlite3
from datetime import datetime, date

# --- DATABASE SETUP ---

def init_db():
    """Initializes the database and ensures all columns exist."""
    conn = sqlite3.connect('habits.db')
    c = conn.cursor()

    # Create table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS habits
    (id INTEGER PRIMARY KEY,
    name TEXT,
    last_completed TEXT,
    streak INTEGER,
    max_streak INTEGER DEFAULT 0)''')

    # Safely add max_streak if the user had an older version of the table
    try:
        c.execute("ALTER TABLE habits ADD COLUMN max_streak INTEGER DEFAULT 0")
    except sqlite3.OperationalError:
        pass

    conn.commit()
    return conn

# --- LOGIC FUNCTIONS ---

def add_habit(conn, name):
    c = conn.cursor()
    c.execute("INSERT INTO habits (name, last_completed, streak, max_streak) VALUES (?, ?, ?, ?)",
    (name, None, 0, 0))
    conn.commit()
    print(f"\n✅ Habit '{name}' added successfully!")

def show_habits(conn):
    c = conn.cursor()
    c.execute("SELECT id, name, streak, max_streak, last_completed FROM habits")
    habits = c.fetchall()

    print(f"\n{'ID':<3} | {'Habit Name':<15} | {'Streak':<7} | {'Record':<7} | {'Last Done'}")
    print("-" * 60)
    for h in habits:
        last_done = h[4] if h[4] else "Never"
        print(f"{h[0]:<3} | {h[1]:<15} | {h[2]:<7} | {h[3]:<7} | {last_done}")

def complete_habit(conn, habit_id):
    c = conn.cursor()
    c.execute("SELECT last_completed, streak, max_streak FROM habits WHERE id = ?", (habit_id,))
    row = c.fetchone()

    if not row:
        print("\n❌ Error: Habit ID not found.")
        return

    last_date_str, current_streak, max_streak = row
    today = date.today()

    # Streak Logic
    if last_date_str:
        last_date = datetime.strptime(last_date_str, '%Y-%m-%d').date()
        delta = (today - last_date).days

        if delta == 0:
            print("\n⚠️ You already completed this today!")
            return
        elif delta == 1:
            current_streak += 1
        else:
            print(f"\n💔 Oh no! You missed {delta-1} day(s). Streak reset.")
        current_streak = 1
    else:
        current_streak = 1 # First time ever

    # Update Personal Best
    new_max = max(current_streak, max_streak)

    c.execute('''UPDATE habits SET last_completed = ?, streak = ?, max_streak = ? WHERE id = ?''',
    (today.isoformat(), current_streak, new_max, habit_id))
    conn.commit()
    print(f"\n⭐ Great job! Current streak: {current_streak} (Personal Best: {new_max})")

def delete_habit(conn, habit_id):
    c = conn.cursor()
    c.execute("DELETE FROM habits WHERE id = ?", (habit_id,))
    conn.commit()
    print(f"\n🗑️ Habit ID {habit_id} deleted.")

# --- MAIN INTERFACE ---

def main():
    conn = init_db()

    while True:
        print("\n===== HABIT TRACKER =====")
        print("1. Add New Habit")
        print("2. Show All Habits")
        print("3. Check-in (Complete Habit)")
        print("4. Delete a Habit")
        print("5. Exit")

        choice = input("\nChoose an option: ")

        if choice == '1':
            name = input("Enter habit name: ")
            if name.strip():
                add_habit(conn, name)
            else:
                print("Name cannot be empty.")

        elif choice == '2':
            show_habits(conn)

        elif choice == '3':
            show_habits(conn)
            try:
                h_id = int(input("\nEnter the ID to check-in: "))
                complete_habit(conn, h_id)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == '4':
            show_habits(conn)
            try:
                h_id = int(input("\nEnter the ID to delete: "))
                confirm = input(f"Are you sure you want to delete ID {h_id}? (y/n): ")
                if confirm.lower() == 'y':
                    delete_habit(conn, h_id)
            except ValueError:
                print("❌ Please enter a valid number.")

        elif choice == '5':
            print("Goodbye! Keep up the good work.")
            conn.close()
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()