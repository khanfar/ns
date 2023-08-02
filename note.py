import sqlite3
import pandas as pd
import winsound
import base64
import os
import shutil
from datetime import datetime
import getpass  # Import getpass module

# Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('notes_db.sqlite')

# Create a cursor object
c = conn.cursor()

# Create table
c.execute('''
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY,
        note TEXT NOT NULL,
        timestamp TEXT NOT NULL
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()

def beep_sound():
    frequency = 1500  # Set frequency To 1500 Hertz
    duration = 500  # Set duration To 500 ms == 0.5 second
    winsound.Beep(frequency, duration)

def encode_note(note):
    return base64.b64encode(note.encode()).decode()

def decode_note(note):
    return base64.b64decode(note).decode()

def add_note_direct(note):
    conn = sqlite3.connect('notes_db.sqlite')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO notes (note, timestamp) VALUES (?, ?)", (encode_note(note), timestamp))
    conn.commit()
    conn.close()
    beep_sound()

def add_note_file(filename):
    if not os.path.exists(filename):
        print("File not found. Please try again.")
        return
    with open(filename, 'r') as file:
        note = file.read()
    conn = sqlite3.connect('notes_db.sqlite')
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute("INSERT INTO notes (note, timestamp) VALUES (?, ?)", (encode_note(note), timestamp))
    conn.commit()
    conn.close()
    beep_sound()
    print("Text file imported successfully.")  # Add success message here

def view_notes():
    conn = sqlite3.connect('notes_db.sqlite')
    c = conn.cursor()
    month = input("Enter a month (1-12) to view notes from that month, or press 'Enter' to view all notes: ")
    if month:
        try:
            month = int(month)
            if month < 1 or month > 12:
                raise ValueError
            year = input("Enter a year: ")
            if not year.isdigit():
                raise ValueError
            c.execute("SELECT * FROM notes WHERE strftime('%m', timestamp) = ? AND strftime('%Y', timestamp) = ?", (str(month).zfill(2), year))
        except ValueError:
            print("Invalid month or year. Please try again.")
            return view_notes()
    else:
        c.execute("SELECT * FROM notes")
    notes = [(id, decode_note(note), timestamp) for id, note, timestamp in c.fetchall()]
    conn.close()
    beep_sound()
    return notes

def search_notes(query):
    conn = sqlite3.connect('notes_db.sqlite')
    c = conn.cursor()
    c.execute("SELECT * FROM notes WHERE note LIKE ?", ('%' + encode_note(query) + '%',))
    notes = [(id, decode_note(note), timestamp) for id, note, timestamp in c.fetchall()]
    conn.close()
    beep_sound()
    return notes

def export_notes(notes, filename):
    with open(filename + '.txt', 'w') as file:
        for note in notes:
            file.write(f'Note: {note[1]}\n\n')  # Write the note followed by two newline characters
    df = pd.DataFrame(notes, columns=['ID', 'Note', 'Timestamp'])
    df = df.drop(columns=['ID', 'Timestamp'])  # Drop the 'ID' and 'Timestamp' columns
    df.to_excel(filename + '.xlsx', index=False)
    beep_sound()

def main():
    for i in range(3, 0, -1):
        beep_sound()
        password = getpass.getpass("Enter the password: ")  # Use getpass to hide the password
        beep_sound()
        if password == '8080':
            break
        else:
            if i > 1:
                print(f"Incorrect password. You have {i-1} attempts left.")
                beep_sound()
                beep_sound()
            else:
                print("Incorrect password. Exiting the program.")
                beep_sound()
                return

    while True:
        print("\n1. Add note")
        print("2. View notes")
        print("3. Search notes")
        print("4. Export all notes")
        print("5. Quit")
        choice = input("Enter your choice: ")
        if choice == '1':
            note_choice = input("Press 'Enter' to input note directly, or '1' to input from a file: ")
            if note_choice == '1':
                filename = input("Enter the filename of your note: ")
                add_note_file(filename)
            else:
                note = input("Enter your note: ")
                add_note_direct(note)
        elif choice == '2':
            notes = view_notes()
            for note in notes:
                print(f'ID: {note[0]}, Note: {note[1]}, Timestamp: {note[2]}')
        elif choice == '3':
            query = input("Enter your search query: ")
            notes = search_notes(query)
            for note in notes:
                print(f'ID: {note[0]}, Note: {note[1]}, Timestamp: {note[2]}')
            export_choice = input("Press 'Enter' to go back to the main menu, or '1' to export the search results: ")
            if export_choice == '1':
                export_notes(notes, 'search_results')
                print("Search results exported successfully.")
        elif choice == '4':
            notes = view_notes()
            export_notes(notes, 'all_notes')
            print("All notes exported successfully.")
        elif choice == '5':
            while True:
                if os.path.exists('G:\\'):
                    shutil.copy('notes_db.sqlite', 'G:\\notes_db.sqlite')
                    print("Database backed up to USB stick successfully.")
                    beep_sound()
                    break
                else:
                    print("No USB stick named 'G:\\' found.")
                    beep_sound()
                    retry_choice = input("Press 'Enter' to try again, or '1' to exit without backing up: ")
                    beep_sound()
                    if retry_choice == '1':
                        break
            break
        else:
            print("Invalid choice. Please try again.")
        beep_sound()

if __name__ == "__main__":
    main()
