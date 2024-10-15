import sqlite3
import datetime

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
        for entry in self.history:
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

    def get_history(self):
        c.execute("SELECT * FROM inventory WHERE item_id=?", (self.item_id,))
        return c.fetchall()


class Inventory:
    def __init__(self):
        self.items = {}
        self.stations = {}

    def add_item(self, item_id, name, owner, weight, description, serial_number, model_number, manufacturer,
                 purchase_date, warranty_info):
        if item_id not in self.items:
            self.items[item_id] = InventoryItem(item_id, name, owner, weight, description, serial_number, model_number,
                                                manufacturer, purchase_date, warranty_info)
        else:
            print("Item ID already exists.")

    def transfer_item(self, item_id, new_owner, station_id):
        if item_id in self.items and station_id in self.stations:
            station_name = self.stations[station_id].name
            self.items[item_id].transfer(new_owner, station_name)
        else:
            print("Item ID or Station ID not found.")

    def get_item_history(self, item_id):
        if item_id in self.items:
            return self.items[item_id].get_history()
        else:
            print("Item ID not found.")
            return None

    def add_station(self, station_id, name):
        if station_id not in self.stations:
            self.stations[station_id] = Station(station_id, name)
            self.stations[station_id].save_to_db()
        else:
            print("Station ID already exists.")


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

print("Laptop History:", inventory.get_item_history(1))
print("Smartphone History:", inventory.get_item_history(2))

# Close the database connection when done
conn.close()
