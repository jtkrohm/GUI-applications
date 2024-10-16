import sqlite3
import datetime
from pyzbar.pyzbar import decode
from PIL import Image

# Connect to SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('inventory.db')
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS inventory
             (item_id INTEGER PRIMARY KEY, name TEXT, owner TEXT, transfer_date TEXT, station TEXT, weight REAL, description TEXT, serial_number TEXT, model_number TEXT, manufacturer TEXT, purchase_date TEXT, warranty_info TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS stations
             (station_id INTEGER PRIMARY KEY, name TEXT)''')


class Station:
    def __init__(self, station_id, name):
        self.station_id = station_id
        self.name = name

    def save_to_db(self):
        c.execute("INSERT INTO stations (station_id, name) VALUES (?, ?)",
                  (self.station_id, self.name))
        conn.commit()


class InventoryItem:
    def __init__(self, item_id, name, owner, weight, description, serial_number, model_number, manufacturer,
                 purchase_date, warranty_info):
        self.item_id = item_id
        self.name = name
        self.owner = owner
        self.weight = weight
        self.description = description
        self.serial_number = serial_number
        self.model_number = model_number
        self.manufacturer = manufacturer
        self.purchase_date = purchase_date
        self.warranty_info = warranty_info
        self.history = [(owner, datetime.datetime.now(), None)]
        self.save_to_db(None)

    def save_to_db(self, station):
        for entry in self.history:   # CRUD
            c.execute(
                "INSERT INTO inventory (item_id, name, owner, transfer_date, station, weight, description, serial_number, model_number, manufacturer, purchase_date, warranty_info) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (
                self.item_id, self.name, entry[0], entry[1], station, self.weight, self.description, self.serial_number,
                self.model_number, self.manufacturer, self.purchase_date, self.warranty_info))
        conn.commit()

    def transfer(self, new_owner, station):
        self.owner = new_owner
        self.history.append((new_owner, datetime.datetime.now(), station))
        self.save_to_db(station)

    def get_history(self): # CRUD
        c.execute("SELECT * FROM inventory WHERE item_id=?", (self.item_id,))
        return c.fetchall()


class Inventory:
    def __init__(self):
        self.items = {}
        self.stations = {}

    def add_item(self, item_id, name, owner, weight, description, serial_number, model_number, manufacturer,
                 purchase_date, warranty_info):
        c.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        existing_item = c.fetchone()
        if existing_item is None:
            self.items[item_id] = InventoryItem(item_id, name, owner, weight, description, serial_number, model_number,
                                                manufacturer, purchase_date, warranty_info)
        else:
            print("Item ID already exists. \n")

    def transfer_item(self, item_id, new_owner, station_id):
        if item_id in self.items and station_id in self.stations:
            station_name = self.stations[station_id].name
            self.items[item_id].transfer(new_owner, station_name)
        else:
            print("Item ID or Station ID not found. \n")

    def get_item_history(self, item_id): # CRUD
        c.execute("SELECT * FROM inventory WHERE item_id=?", (item_id,))
        return c.fetchall()

    def get_item_status(self, item_id):
        item_history = self.get_item_history(item_id)
        if item_history:
            latest_record = item_history[-1]  # Last record in the history
            return {
                'Owner': latest_record[2],
                'Date': latest_record[3],
                'Station': latest_record[4]
            }
        else:
            return "Item ID not found."

    def print_item_history(self, item_id):
        item_history = self.get_item_history(item_id)
        if item_history:
            for record in item_history:
                print(f"Owner: {record[2]}, Date: {record[3]}, Station: {record[4]} \n")
        else:
            print("Item ID not found. \n")

    def add_station(self, station_id, name):
        c.execute("SELECT * FROM stations WHERE station_id=?", (station_id,))
        existing_station = c.fetchone()
        if existing_station is None:
            self.stations[station_id] = Station(station_id, name)
            self.stations[station_id].save_to_db()
        else:
            print("Station ID already exists. \n")

    def scan_barcode(self, image_path):
        image = Image.open(image_path)
        barcodes = decode(image)
        if barcodes:
            for barcode in barcodes:
                barcode_data = barcode.data.decode("utf-8")
                print("Scanned Barcode Data:", barcode_data, "\n")
                return barcode_data
        else:
            print("No barcodes found. \n")
            return None


# Example usage
inventory = Inventory()
inventory.add_station(1, "Main Office")
inventory.add_station(2, "Warehouse")

inventory.add_item(1, "Laptop", "Alice", 2.5, "15-inch laptop", "SN123456", "MN987654", "TechCo", "2023-01-15",
                   "2 years warranty")
inventory.add_item(2, "Smartphone", "Bob", 0.5, "Latest model smartphone", "SN654321", "MN123987", "MobileCorp",
                   "2022-05-20", "1 year warranty")

inventory.transfer_item(1, "Charlie", 1)
inventory.transfer_item(2, "Diana", 2)

print("Laptop History:")
inventory.print_item_history(1)

print("Smartphone History:")
inventory.print_item_history(2)

# Check the latest status
item_status = inventory.get_item_status(1)
print(item_status)

# Close the database connection when done
conn.close()
