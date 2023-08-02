import sqlite3
from datetime import datetime, timedelta
from sqlite3 import Error
import pytz
import sqlite3
import os 
import winsound
import pandas as pd
import getpass
from tabulate import tabulate
from prettytable import PrettyTable
import shutil




def get_adjusted_time(offset_hours):
    utc_now = datetime.now(pytz.utc)
    local_now = utc_now.astimezone(pytz.timezone('Asia/Amman'))
    adjusted_time = local_now + timedelta(hours=offset_hours)
    return adjusted_time.strftime('%Y-%m-%d %H:%M:%S')

# Example usage:
offset_hours = 0  # Adjust the offset as needed
adjusted_time = get_adjusted_time(offset_hours)
print(adjusted_time)




LICENSE_KEYS = ['80808080', '80808081', '80808082', '80808083']
LICENSE_KEYS_PATH = 'C:\\Windows.txt'

def int_to_binary_x2(number):
    binary_number = format(number, 'b')
    doubled_binary = int(binary_number) * 2
    return str(doubled_binary)

def get_license_key():
    """
    Prompt the user to enter a license key and validate it
    """
    while True:
        key = input("Enter your license key: ")
        if key in LICENSE_KEYS:
            LICENSE_KEYS.remove(key)
            binary_license_keys = [int_to_binary_x2(int(k)) for k in LICENSE_KEYS]
            with open(LICENSE_KEYS_PATH, 'w') as f:
                f.write('\n'.join(binary_license_keys))
            print("License key accepted")
            return True
        else:
            print("Invalid license key")
            beep_sound()

def check_license():
    """
    Check if a valid license key exists
    """
    if os.path.exists(LICENSE_KEYS_PATH):
        with open(LICENSE_KEYS_PATH, 'r') as f:
            license_keys = f.read().splitlines()
        if license_keys:
            return True
    return False

if not check_license():
    get_license_key()
    
def login():
    password = "8080"  # The password to login
    for i in range(3, 0, -1):
        input_password = getpass.getpass("Enter password: ")
        if input_password == password:
            return True
        else:
            print(f"Incorrect password. You have {i-1} attempts left.")
            beep_sound()
            beep_sound()
    return False


# Beep sound
def beep_sound():
    frequency = 1500  # Set frequency To 2500 Hertz
    duration = 500  # Set duration To 1000 ms == 1 second
    winsound.Beep(frequency, duration)
def create_connection(db_file):
    """ create a database connection to a SQLite database """
    conn = None;
    try:
        conn = sqlite3.connect(db_file)
        print(sqlite3.version)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

def backup_database():
    source = 'truck_maintenance.db'
    current_time = datetime.now().strftime("%Y%m%d%H%M%S")  # get current date and time
    destination = f'G:/truck_maintenance_backup_{current_time}.db'

    while True:
        if os.path.exists('G:'):
            shutil.copy2(source, destination)
            print(f"Database has been backed up to USB drive as {destination}.")
            beep_sound()
            beep_sound()
            break
        else:
            print("USB drive G: not found.")
            beep_sound()
            beep_sound()
            choice = input("Do you want to retry? 1- Retry, any key - Exit: ")
            if choice != '1':
                break

# Database setup
def create_tables():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS trucks (
    id INTEGER PRIMARY KEY,
    plate_number TEXT NOT NULL,
    owner_name TEXT NOT NULL,
    driver_name TEXT NOT NULL,
    truck_type TEXT NOT NULL,
    phone TEXT NOT NULL)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY,
    truck_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    record_text TEXT NOT NULL,
    FOREIGN KEY (truck_id) REFERENCES trucks (id))''')
    conn.commit()
    conn.close()

# Add a new truck
def add_truck():
    plate_number = input("Enter Plate Number: ")
    if not plate_number:  # Check if plate_number is empty
        print("Plate number cannot be empty.")
        beep_sound()
        beep_sound()
        return  # Exit the function
    owner_name = input("Enter Owner Name: ")
    driver_name = input("Enter Driver Name: ")
    truck_type = input("Enter Truck Type: ")
    phone = input("Enter Phone: ")
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO trucks (plate_number, owner_name, driver_name, truck_type, phone) VALUES (?, ?, ?, ?, ?)', (plate_number, owner_name, driver_name, truck_type, phone))
    conn.commit()
    conn.close()


# Update truck information based on license plate number
def update_truck():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    plate_number = input("Enter current Plate Number: ")
    cursor.execute('SELECT id FROM trucks WHERE plate_number=?', (plate_number,))
    truck_id = cursor.fetchone()
    if truck_id is not None:
        new_plate_number = input("Enter new Plate Number: ")
        owner_name = input("Enter Owner Name: ")
        driver_name = input("Enter Driver Name: ")
        truck_type = input("Enter Truck Type: ")
        phone = input("Enter Phone: ")
        cursor.execute('UPDATE trucks SET plate_number=?, owner_name=?, driver_name=?, truck_type=?, phone=? WHERE id=?', 
                       (new_plate_number, owner_name, driver_name, truck_type, phone, truck_id[0]))
        conn.commit()
        print(f"Updated truck with plate number {plate_number}")
        beep_sound()
    else:
        print(f"No truck found with plate number {plate_number}")
        beep_sound()
        beep_sound()
    conn.close()






# Delete a truck based on license plate number
def delete_truck(plate_number):
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id FROM trucks WHERE plate_number=?', (plate_number,))
    truck_id = cursor.fetchone()
    if truck_id is not None:
        confirm = input(f"Are you sure you want to delete the truck with plate number {plate_number}? (y/n): ")
        if confirm.lower() == 'y':
            cursor.execute('DELETE FROM trucks WHERE id=?', (truck_id[0],))
            cursor.execute('DELETE FROM records WHERE truck_id=?', (truck_id[0],))
            conn.commit()
            print(f"Deleted truck with plate number {plate_number}")
            beep_sound()
        else:
            print("Deletion cancelled.")
            beep_sound()
    else:
        print(f"No truck found with plate number {plate_number}")
        beep_sound()
    conn.close()



# Add a record based on license plate number
def add_record():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    plate_number = input("Enter Plate Number: ")
    cursor.execute('SELECT id FROM trucks WHERE plate_number=?', (plate_number,))
    truck_id = cursor.fetchone()
    if truck_id is not None:
        # Fetch the last record for this truck
        cursor.execute('SELECT * FROM records WHERE truck_id=? ORDER BY date DESC LIMIT 1', (truck_id[0],))
        last_record = cursor.fetchone()
        if last_record is not None:
            print(f"Last record date and time for this truck: {last_record[2]}")
            beep_sound()
            print(f"Last record text: {last_record[3]}")  # print the last record text
            beep_sound()
            proceed = input("Do you want to add a new record? (y/n): ")
            if proceed.lower() != 'y':
                print("Operation cancelled.")
                beep_sound()
                return
        else:
            print("No records found for this truck.")
            beep_sound()

        record_text = input("Enter Record Text: ")
        adjusted_time = get_adjusted_time(0)  # Get the adjusted time with an offset of +3 hours
        cursor.execute('INSERT INTO records (truck_id, date, record_text) VALUES (?, ?, ?)', (truck_id[0], adjusted_time, record_text))
        conn.commit()
        print(f"Added record for truck with plate number {plate_number}")
        beep_sound()
    else:
        print(f"No truck found with plate number {plate_number}")
        beep_sound()
    conn.close()




# Update a record based on license plate number
def update_record():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    plate_number = input("Enter Plate Number: ")
    cursor.execute('SELECT id FROM trucks WHERE plate_number=?', (plate_number,))
    truck_id = cursor.fetchone()
    if truck_id is not None:
        cursor.execute('''SELECT records.id, records.date, records.record_text, trucks.plate_number
                          FROM records
                          JOIN trucks ON records.truck_id = trucks.id
                          WHERE truck_id=?''', (truck_id[0],))
        records = cursor.fetchall()
        for record in records:
            print(f'ID: {record[0]}, Plate Number: {record[3]}, Date: {record[1]}, Record: {record[2]}')
        record_id = input("Enter Record ID to update: ")
        cursor.execute('SELECT id FROM records WHERE id=?', (record_id,))
        record_check = cursor.fetchone()
        if record_check is None:
            print("Record ID does not exist.")
            beep_sound()
            return
        new_record_text = input("Enter new record text: ")
        confirm = input(f"Are you sure you want to update the record with ID {record_id}? (y/n): ")
        if confirm.lower() == 'y':
            cursor.execute('UPDATE records SET record_text=? WHERE id=?', (new_record_text, record_id))
            conn.commit()
            print(f"Updated record with ID {record_id}")
            beep_sound()
        else:
            print("Update cancelled.")
            beep_sound()
    else:
        print(f"No records found for plate number {plate_number}")
        beep_sound()
        beep_sound()
    conn.close()



# Delete a record based on license plate number
def delete_record():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    plate_number = input("Enter Plate Number: ")
    cursor.execute('SELECT id FROM trucks WHERE plate_number=?', (plate_number,))
    truck_id = cursor.fetchone()
    if truck_id is not None:
        cursor.execute('''SELECT records.id, records.date, records.record_text, trucks.plate_number
                          FROM records
                          JOIN trucks ON records.truck_id = trucks.id
                          WHERE truck_id=?''', (truck_id[0],))
        records = cursor.fetchall()
        for record in records:
            print(f'ID: {record[0]}, Plate Number: {record[3]}, Date: {record[1]}, Record: {record[2]}')
            
        record_id = input("Enter Record ID to delete: ")
        cursor.execute('SELECT id FROM records WHERE id=?', (record_id,))
        record_check = cursor.fetchone()
        if record_check is None:
            print("Record ID does not exist.")
            beep_sound()
            return
        confirm = input(f"Are you sure you want to delete the record with ID {record_id}? (y/n): ")
        if confirm.lower() == 'y':
            cursor.execute('DELETE FROM records WHERE id=?', (record_id,))
            conn.commit()
            print(f"Deleted record with ID {record_id}")
            beep_sound()
        else:
            print("Deletion cancelled.")
            beep_sound()
    else:
        print(f"No records found for plate number {plate_number}")
        beep_sound()
    conn.close()



# List all trucks
def list_trucks():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()

    view_today = input("Do you want to view the truck list for active Records today? (1/no): ")
    if view_today.lower() == '1':
        # Get today's date
        today = datetime.today().strftime('%Y-%m-%d')

        # Query to get trucks that have a record added today
        cursor.execute("""
            SELECT t.* 
            FROM trucks t
            JOIN records r ON t.id = r.truck_id
            WHERE DATE(r.date) = ?
        """, (today,))
    else:
        # Existing query to get all trucks
        cursor.execute('SELECT * FROM trucks')

    trucks = cursor.fetchall()
    for truck in trucks:
        print(f'ID: {truck[0]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}')

    conn.close()



# Function to display a single record box
def display_record_box(record):
    box = PrettyTable()
    box.field_names = ['ID', 'Date', 'Plate Number', 'Owner Name', 'Driver Name', 'Truck Type', 'Phone', 'Record']
    box.add_row(record)
    print(box)



def get_all_owner_names():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    cursor.execute('SELECT DISTINCT owner_name FROM trucks')
    owners = cursor.fetchall()
    conn.close()
    return [owner[0] for owner in owners]


def export_data_based_on_owner():
    owners = get_all_owner_names()
    print("Owner Names:")
    for i, owner in enumerate(owners, start=1):
        print(f"{i}. {owner}")
    owner_choice = input("Choose an owner by number: ")
    if not owner_choice.isdigit() or int(owner_choice) < 1 or int(owner_choice) > len(owners):
        print("Invalid choice. Please choose a number from the list.")
        return
    owner_name = owners[owner_choice - 1]

    print("1. Export based on month")
    print("2. Export based on day")
    export_choice = input("Choose an export option by number: ")

    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()

    try:
        if export_choice == '1':
            month_year = input("Enter Month and Year (mmYYYY): ")
            formatted_month = datetime.strptime(month_year, '%m%Y').strftime('%Y-%m')
            cursor.execute('''SELECT records.id, records.date, trucks.owner_name, trucks.truck_type, trucks.plate_number, records.record_text
                            FROM records
                            JOIN trucks ON records.truck_id = trucks.id
                            WHERE date LIKE ? AND owner_name = ?''', (f'{formatted_month}%', owner_name))
        elif export_choice == '2':
            date = input("Enter Date (ddmmyyyy): ")
            formatted_date = datetime.strptime(date, '%d%m%Y').strftime('%Y-%m-%d')
            cursor.execute('''SELECT records.id, records.date, trucks.owner_name, trucks.truck_type, trucks.plate_number, records.record_text
                            FROM records
                            JOIN trucks ON records.truck_id = trucks.id
                            WHERE date LIKE ? AND owner_name = ?''', (f'{formatted_date}%', owner_name))
        else:
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid date format. Please enter the date as mmYYYY for month or ddmmyyyy for day.")
        return

    records = cursor.fetchall()
    if not records:
        print("No records found for the given date and owner.")
        return

    data = []  # list to hold the data
    for record in records:
        data.append({
            'ID': record[0],
            'Date': record[1],
            'Owner Name': record[2],
            'Truck Type': record[3],
            'Plate Number': record[4],
            'Record': record[5]
        })
    df = pd.DataFrame(data)  # create a DataFrame from the data
    df.to_excel(f'records_{owner_name}_{formatted_month if export_choice == "1" else formatted_date}.xlsx', index=False)  # write the DataFrame to an Excel file
    print(f"All records for {owner_name} have been written to 'records_{owner_name}_{formatted_month if export_choice == '1' else formatted_date}.xlsx'")
    beep_sound()
    beep_sound()

    conn.close()







# List records based on user's choice
def list_records():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    print("1. List using license plate number")
    print("2. List using owner name")
    print("3. List all records in specific day")
    print("4. Extract all records in specific day to a text file")
    print("5. Extract all records in specific day to an Excel file")
    print("6. List all records in specific month")
    print("7. Extract all records in specific month to a text file")
    print("8. Extract all records in specific month to an Excel file")
    print("9. Export data based on owner name")
    choice = input("Enter your choice: ")
    if choice == '1':
        plate_number = input("Enter Plate Number: ")
        cursor.execute('''SELECT records.id, records.date, records.record_text, trucks.plate_number
                          FROM records
                          JOIN trucks ON records.truck_id = trucks.id
                          WHERE plate_number=?''', (plate_number,))
        records = cursor.fetchall()
        if not records:  # Check if the records list is empty
            print("No records found for that license plate.")
            beep_sound()
            return  # Exit the function early

        for record in records:
            print(f'ID: {record[0]}, Plate Number: {record[3]}, Date: {record[1]}, Record: {record[2]}')
            
        # Fetch the truck data
        cursor.execute('SELECT * FROM trucks WHERE plate_number=?', (plate_number,))
        truck = cursor.fetchone()

        # Print the truck data
        print(f'ID: {truck[0]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}')
        




        # Ask the user if they want to export the data
        export_choice = input("Do you want to export the data? (1 for Excel, 2 for Text, any other key to skip): ")
        if export_choice == '1':
            # Export to Excel
            data = []
            # Add truck details to the data
            data.append({
                'ID': truck[0],
                'Plate Number': truck[1],
                'Owner Name': truck[2],
                'Truck Type': truck[4],
                'Phone': truck[5]

            })
            

            for record in records:
                data.append({
                    'ID': record[0],
                    'Date': record[1],
                    'Record': record[2]
                })
            df = pd.DataFrame(data)
            df.to_excel(f'records_{plate_number}.xlsx', index=False)
            print(f"All records for {plate_number} have been written to 'records_{plate_number}.xlsx'")
            beep_sound()
            beep_sound()
            
            
        elif export_choice == '2':
            # Export to Text
            with open(f'records_{plate_number}.txt', 'w') as f:
                # Write truck details to the file
                f.write(f'ID: {truck[0]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Truck Type: {truck[4]}, Phone: {truck[5]}\n')
                for record in records: 
                    f.write(f'ID: {record[0]}, Plate Number: {record[3]}, Date: {record[1]}, Record: {record[2]}\n')  
            print(f"All records for {plate_number} have been written to 'records_{plate_number}.txt'")
            beep_sound()
            beep_sound()
    
    elif choice == '2':
        # Get all distinct owner names
        cursor.execute('SELECT DISTINCT owner_name FROM trucks')
        owners = cursor.fetchall()
        owners = [owner[0] for owner in owners]

        # Print all owner names
        print("Owner Names:")
        for i, owner in enumerate(owners, start=1):
            print(f"{i}. {owner}")

        # Let the user choose an owner
        owner_choice = int(input("Choose an owner by number: "))
        if owner_choice < 1 or owner_choice > len(owners):
            print("Invalid choice. Please choose a number from the list.")
            return
        owner_name = owners[owner_choice - 1]

        # Get and print all records for the chosen owner
        cursor.execute('''SELECT records.id, records.date, trucks.owner_name, trucks.truck_type, trucks.plate_number, records.record_text
                          FROM records
                          JOIN trucks ON records.truck_id = trucks.id
                          WHERE owner_name = ?''', (owner_name,))
        records = cursor.fetchall()
        for record in records:
            print(f"ID: {record[0]}, Date: {record[1]}, Owner Name: {record[2]}, Truck Type: {record[3]}, Plate Number: {record[4]}, Record: {record[5]}")
    elif choice == '9':
        export_data_based_on_owner() 
            
    elif choice == '3':
        date = input("Enter Date (ddmmyyyy): ")
        try:
            formatted_date = datetime.strptime(date, '%d%m%Y').strftime('%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter date as ddmmyyyy.")
            return
        
        cursor.execute('''SELECT records.date, trucks.owner_name, trucks.truck_type, trucks.plate_number, records.record_text
                       FROM records
                       JOIN trucks ON records.truck_id = trucks.id
                       WHERE date LIKE ?''', (f'{formatted_date}%',))
        records = cursor.fetchall()

        if not records:  # Check if the records list is empt
            print("No records found for that date.")
            return  # Exit the function early
        
        for record in records:
            print(f"Date: {record[0]}, Owner Name: {record[1]}, Truck Type: {record[2]}, Plate Number: {record[3]}, Record: {record[4]}")
        


            

    elif choice == '4':
        date = input("Enter Date (ddmmyyyy): ")
        try:
            formatted_date = datetime.strptime(date, '%d%m%Y').strftime('%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter date as ddmmyyyy.")
            return

        cursor.execute('SELECT * FROM records WHERE date LIKE ?', (f'{formatted_date}%',))
        records = cursor.fetchall()
        with open(f'records_{formatted_date}.txt', 'w') as f:
            f.write('----------- ARAFAT Garage ------------\n')
            f.write(f'------- Total reports: {len(records)}, Date: {formatted_date} --------\n')
            for record in records:
                cursor.execute('SELECT * FROM trucks WHERE id=?', (record[1],))
                truck = cursor.fetchone()
                f.write(f'ID: {record[0]}, Truck ID: {record[1]}, Date: {record[2]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}, Record: {record[3]}\n')
        print(f"All records for {formatted_date} have been written to 'records_{formatted_date}.txt'")
        beep_sound()
        beep_sound()
        
        



    elif choice == '5':
        date = input("Enter Date (ddmmyyyy): ")
        try:
            formatted_date = datetime.strptime(date, '%d%m%Y').strftime('%Y-%m-%d')
        except ValueError:
            print("Invalid date format. Please enter date as ddmmyyyy.")
            return
        cursor.execute('SELECT * FROM records WHERE date LIKE ?', (f'{formatted_date}%',))
        records = cursor.fetchall()
        data = []  # list to hold the data
        for record in records:
            cursor.execute('SELECT * FROM trucks WHERE id=?', (record[1],))
            truck = cursor.fetchone()
            data.append({
                'ID': record[0],
                'Truck ID': record[1],
                'Date': record[2],
                'Phone': truck[5],
                'Plate Number': truck[1],
                'Owner Name': truck[2],
                'Driver Name': truck[3],
                'Truck Type': truck[4],
                'Record': record[3],
            })
        df = pd.DataFrame(data)  # create a DataFrame from the data
        df.to_excel(f'records_{formatted_date}.xlsx', index=False)  # write the DataFrame to an Excel file
        print(f"All records for {formatted_date} have been written to 'records_{formatted_date}.xlsx'")
        beep_sound()
        beep_sound()
        
        

    elif choice == '6':  # new elif branch
        month_year = input("Enter Month and Year (mmYYYY): ")
        formatted_month = datetime.strptime(month_year, '%m%Y').strftime('%Y-%m')
        cursor.execute('SELECT * FROM records WHERE date LIKE ?', (f'{formatted_month}%',))
        records = cursor.fetchall()
        for record in records:
            cursor.execute('SELECT * FROM trucks WHERE id=?', (record[1],))
            truck = cursor.fetchone()
            print(f'ID: {record[0]}, Truck ID: {record[1]}, Plate Number: {truck[1]}, Date: {record[2]}, Record: {record[3]}')
            

    elif choice == '7':  # new elif branch
        month_year = input("Enter Month and Year (mmYYYY): ")
        try:
            formatted_month = datetime.strptime(month_year, '%m%Y').strftime('%Y-%m')
        except ValueError:
            print("Invalid date format. Please enter month and year as mmYYYY.")
            return    

        
        cursor.execute('SELECT * FROM records WHERE date LIKE ?', (f'{formatted_month}%',))
        records = cursor.fetchall()
        with open(f'records_{formatted_month}.txt', 'w') as f:
            f.write('----------- ARAFAT Garage ------------\n')
            f.write(f'------- Total reports: {len(records)}, Month: {formatted_month} --------\n')
            for record in records:
                cursor.execute('SELECT * FROM trucks WHERE id=?', (record[1],))
                truck = cursor.fetchone()
                f.write(f'ID: {record[0]}, Truck ID: {record[1]}, Date: {record[2]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}, Record: {record[3]}\n')
        print(f"All records for {formatted_month} have been written to 'records_{formatted_month}.txt'")
        beep_sound()
        beep_sound()
        
        

    elif choice == '8':  # new elif branch
        month_year = input("Enter Month and Year (mmYYYY): ")
        try:
            formatted_month = datetime.strptime(month_year, '%m%Y').strftime('%Y-%m')
        except ValueError:
            print("Invalid date format. Please enter month and year as mmYYYY.")
            return    
        cursor.execute('SELECT * FROM records WHERE date LIKE ?', (f'{formatted_month}%',))
        records = cursor.fetchall()
        data = []  # list to hold the data
        for record in records:
            cursor.execute('SELECT * FROM trucks WHERE id=?', (record[1],))
            truck = cursor.fetchone()
            data.append({
                'ID': record[0],
                'Truck ID': record[1],
                'Date': record[2],
                'Plate Number': truck[1],
                'Owner Name': truck[2],
                'Driver Name': truck[3],
                'Truck Type': truck[4],
                'Phone': truck[5],
                'Record': record[3]
            })
        df = pd.DataFrame(data)  # create a DataFrame from the data
        df.to_excel(f'records_{formatted_month}.xlsx', index=False)  # write the DataFrame to an Excel file
        print(f"All records for {formatted_month} have been written to 'records_{formatted_month}.xlsx'")
        beep_sound()
        beep_sound()
        
    elif choice == '9':    # export txt and excel file based on owner name 
        export_data_based_on_owner()


    else:
        print("Invalid choice.")
        beep_sound()
    conn.close()
   
    


# Search for a truck 
def search_truck():
    conn = sqlite3.connect('truck_maintenance.db')
    cursor = conn.cursor()
    plate_number = input("Enter Plate Number: ")
    cursor.execute('SELECT * FROM trucks WHERE plate_number=?', (plate_number,))
    truck = cursor.fetchone()
    if truck is not None:
        print(f'ID: {truck[0]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}')
        
    else:
        print(f"No truck found with plate number {plate_number}")
        beep_sound()
        beep_sound()
    conn.close()







# Print truck details
def print_truck(truck):
    print(f'ID: {truck[0]}, Plate Number: {truck[1]}, Owner Name: {truck[2]}, Driver Name: {truck[3]}, Truck Type: {truck[4]}, Phone: {truck[5]}')

# Main function
def main():
    create_tables()
    # Login system
    if not login():
        print("Invalid password. Exiting...")
        beep_sound()
        return
    # Welcome message
    import time
    welcome_message = "Welcome to Mhanfar Development Software 0598761745 ...  E4MWAK@GMAIL.COM  copyright © 2023 all rights reserved   "
    for i in range(5):
        print(welcome_message, end='\r')
        time.sleep(1)
    print(' ' * len(welcome_message), end='\r')  # Clear the welcome message
    beep_sound()  # Beep sound
    while True:
        # The rest of your code...

        print   ( "   *************************************************** " )
        print   ( "      *****   نظام إدارة الشاحنات   ***** " )
        print   ( "   ***************************************************  " )
        print   (                             "برمجة m-khanfar <0598761745> "      )
        print( "-----------------------------------------------------------"  )
        print(   )
        print("\n1. Add Truck\n2. Update Truck\n3. Delete Truck\n4. Add Record\n5. Update Record\n6. Delete Record\n7. List Trucks\n8. List Records\n9. Search Truck\n0. Exit")
        choice = input("Enter your choice: ")
        if choice == '1':
            add_truck()
        
        
        elif choice == '2':
            update_truck()


        elif choice == '3':
            truck_id = input("Enter Truck ID: ")
            delete_truck(truck_id)
        elif choice == '4':
            add_record()
        elif choice == '5':
            update_record()
        elif choice == '6':
            delete_record()
        elif choice == '7':
            list_trucks()
        elif choice == '8':
            list_records()
        elif choice == '9':
            search_truck()
        elif choice == '0':
            print("Please insert your USB and press any key to continue...")
            beep_sound()
            backup_database() # call the backup_database function here
            break
        else:
            print("Invalid choice. Please try again.")
            beep_sound()
            beep_sound()





if __name__ == "__main__":
    create_connection("truck_maintenance.db")
    main()  # call your main function here




