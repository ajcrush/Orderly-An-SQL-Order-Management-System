import tkinter as tk
from tkinter import messagebox, simpledialog
import sqlite3

class MenuOrderSystem:
    def __init__(self):
        # Connect to the SQLite database
        self.conn = sqlite3.connect("menu_order_system.db")
        self.cursor = self.conn.cursor()
        
        # Create Orders table if it doesn't exist
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS Orders (
                order_id INTEGER PRIMARY KEY,
                customer_name TEXT,
                items TEXT
            )
        """)
        self.conn.commit()

    def add_order(self, order_id, customer_name, items):
        try:
            self.cursor.execute("INSERT INTO Orders (order_id, customer_name, items) VALUES (?, ?, ?)",
                                (order_id, customer_name, ', '.join(items)))
            self.conn.commit()
            return f"Order {order_id} added for {customer_name}."
        except sqlite3.IntegrityError:
            return "Order ID must be unique."

    def serve_order(self):
        self.cursor.execute("SELECT * FROM Orders ORDER BY order_id LIMIT 1")
        order = self.cursor.fetchone()
        if order is None:
            return "No orders to serve."
        
        self.cursor.execute("DELETE FROM Orders WHERE order_id = ?", (order[0],))
        self.conn.commit()
        return f"Serving order {order[0]} for {order[1]}."

    def display_orders(self):
        self.cursor.execute("SELECT * FROM Orders")
        orders = self.cursor.fetchall()
        if not orders:
            return "No current orders."
        return "\n".join([f"Order ID: {o[0]}, Customer: {o[1]}, Items: {o[2]}" for o in orders])

    def estimated_waiting_time(self, order_id):
        self.cursor.execute("SELECT items FROM Orders WHERE order_id = ?", (order_id,))
        order = self.cursor.fetchone()
        if order is None:
            return "Order not found."
        
        average_prep_time = 5  # average time in minutes per item
        item_count = len(order[0].split(', '))
        waiting_time = item_count * average_prep_time
        return f"Estimated waiting time for order {order_id} is approximately {waiting_time} minutes."

    def close(self):
        self.conn.close()

class MenuOrderApp:
    def __init__(self, root):
        self.menu_system = MenuOrderSystem()
        self.root = root
        self.root.title("Menu Order System")
        
        # Create and place the UI elements
        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Menu Order System", font=("Helvetica", 16)).pack(pady=10)

        self.add_order_button = tk.Button(self.root, text="Add Order", command=self.add_order)
        self.add_order_button.pack(pady=5)

        self.serve_order_button = tk.Button(self.root, text="Serve Order", command=self.serve_order)
        self.serve_order_button.pack(pady=5)

        self.display_orders_button = tk.Button(self.root, text="Display Orders", command=self.display_orders)
        self.display_orders_button.pack(pady=5)

        self.estimated_waiting_time_button = tk.Button(self.root, text="Estimated Waiting Time", command=self.check_waiting_time)
        self.estimated_waiting_time_button.pack(pady=5)

        self.exit_button = tk.Button(self.root, text="Exit", command=self.exit_application)
        self.exit_button.pack(pady=5)

    def add_order(self):
        order_id = simpledialog.askinteger("Input", "Enter order ID:")
        customer_name = simpledialog.askstring("Input", "Enter customer name:")
        items = simpledialog.askstring("Input", "Enter items (comma-separated):")
        if order_id is not None and customer_name and items:
            items_list = [item.strip() for item in items.split(',')]
            message = self.menu_system.add_order(order_id, customer_name, items_list)
            messagebox.showinfo("Info", message)

    def serve_order(self):
        message = self.menu_system.serve_order()
        messagebox.showinfo("Info", message)

    def display_orders(self):
        orders = self.menu_system.display_orders()
        messagebox.showinfo("Current Orders", orders)

    def check_waiting_time(self):
        order_id = simpledialog.askinteger("Input", "Enter order ID to check waiting time:")
        if order_id is not None:
            message = self.menu_system.estimated_waiting_time(order_id)
            messagebox.showinfo("Waiting Time", message)

    def exit_application(self):
        self.menu_system.close()
        self.root.quit()

def main():
    root = tk.Tk()
    app = MenuOrderApp(root)
    root.mainloop()

# Run the main function if the script is executed directly
if __name__ == "__main__":
    main()