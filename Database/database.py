import sqlite3
from datetime import datetime

class Database:
    def __init__(self, database):
        self.database = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.database.cursor()

    def time_range(self, table, condition_column, condition_value):
        try:
            time_format = "%Y-%m-%d %H:%M:%S"
            start = self.get_value("start_time", table, condition_column, condition_value)
            start_time = datetime.strptime(start, time_format)
            end = self.get_value("end_time", table, condition_column, condition_value)
            end_time = datetime.strptime(end, time_format)
            current_time = datetime.now()

            if start_time <= current_time <= end_time:
                return True
            else:
                return False
        except sqlite3.Error as e:
            print(f"error: {e}")

    def element_exist(self, table, column, value):
        query = f"SELECT EXISTS(SELECT 1 FROM {table} WHERE {column} = ?)"
        exist = self.cursor.execute(query, (value,))
        exist = exist.fetchone()[0]
        return bool(exist)

    
    def get_value(self, column: str, table: str , condition_column: str, condition_value: any):
        try:
            query = f"""SELECT {column} FROM {table} WHERE {condition_column}=?"""
            value = self.cursor.execute(query, (condition_value,)).fetchone()
            if value is not None:
                return value[0]  # Extract and return the actual column value
            else:
                print(f"No record found in {table} where {condition_column}={condition_value}")
                return None  # Return None if no record found
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")
            return None

        
    def switch_status(self, table: str, column: str, condition_column: str, condition_value: int):
        try:
            query = f"""
                UPDATE {table}
                SET {column} = CASE 
                    WHEN {column} = 1 THEN 0
                    ELSE 1
                END
                WHERE {condition_column} = ?"""
            self.cursor.execute(query, (condition_value,))
            self.database.commit()
            print(f"Successfully toggled {column} for {condition_column} = {condition_value}.")
        except sqlite3.Error as e:
            print(f"Database error occurred: {e}")



    def reserving(self, plate_number: str, spot_id: int, start_time: str, end_time: str):
        try:
            check = self.get_value("is_reserved", "parking_spots", "spot_id", spot_id)
            if check == 0:
                self.cursor.execute("""
                    INSERT INTO reservations ("plate_number", "spot_id", "start_time", "end_time") 
                    VALUES (?, ?, ?, ?)""", 
                    (plate_number, spot_id, start_time, end_time))

                # Mark the spot as reserved
                self.switch_status("parking_spots", "is_reserved", "spot_id", spot_id)
                self.database.commit()
                print("Success Reservation")
            else:
                print(f"Error: Spot {spot_id} is already reserved.")
        except sqlite3.Error as e:
            print(f"Error: {e}")

    def checkin(self, plate_number: str):
        try: 
            print("1")
            if self.element_exist("reservations", "plate_number", plate_number) and self.time_range("reservations", "plate_number", plate_number):
                    status = self.get_value("status", "reservations", "plate_number", plate_number)
                    spot = self.get_value("spot_id", "reservations", "plate_number", plate_number)
                    print("a")
                    
                    match status:
                        case "Reserved":  # CHECK IN
                            self.switch_status("parking_spots", "is_occupied", "spot_id", spot)
                            query = """UPDATE reservations SET status = "Checked-In" WHERE plate_number = ?"""
                            self.cursor.execute(query, (plate_number,))
                            self.database.commit()
                            print("Successful Check-in")
                            return "Check-in"
                            
                        
                        case "Checked-In":  # CHECK OUT
                            self.switch_status("parking_spots", "is_reserved", "spot_id", spot)
                            self.switch_status("parking_spots", "is_occupied", "spot_id", spot)
                            query = """DELETE FROM reservations WHERE plate_number = ?"""
                            self.cursor.execute(query, (plate_number,))
                            self.database.commit()
                            print("Successful Check-out")
                            return "Check-out"
                        
            
                        case _:
                            print(f"Invalid status '{status}' for plate number {plate_number}")
            return "False"
                
            
        except sqlite3.Error as e:
            return e


    def close(self):
        self.database.close()