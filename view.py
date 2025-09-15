import tkinter as tk
from tkinter import ttk, messagebox

class MainAppView(tk.Tk):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.title("Car Decor Shop Manager")
        self.dashboard = None
        # Move the window off-screen to make it invisible but active
        self.geometry("400x250+5000+5000")

    def show_dashboard(self, user_role):
        """Builds the dashboard and then centers the main window."""
        if user_role == 'admin':
            self.dashboard = AdminDashboard(self, self.controller)
        else:
            self.dashboard = StdUserDashboard(self, self.controller)
        self.center_on_screen()

    def center_on_screen(self):
        """Centers the main window on the user's screen."""
        self.deiconify()
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

class LoginWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Login")
        self.geometry("300x150+300+300")
        self.transient(parent)
        self.grab_set()

        ttk.Label(self, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(self)
        self.username_entry.pack(pady=5, padx=10, fill='x')
        ttk.Label(self, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(self, show="*")
        self.password_entry.pack(pady=5, padx=10, fill='x')
        ttk.Button(self, text="Login", command=self.login).pack(pady=10)
        self.username_entry.focus()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_login(username, password, self)

# --- Base Dashboard Frame (UPDATED) ---
class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=10, pady=10)
        parent.geometry("800x600")
        self.selected_record_id = None
        self.create_ui()

    def create_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', pady=5)
        
        # This frame holds the action buttons
        action_buttons_frame = ttk.Frame(top_frame)
        action_buttons_frame.pack(side='left')
        self.create_buttons(action_buttons_frame)

        # --- NEW: View Details Button ---
        self.view_details_button = ttk.Button(top_frame, text="View Details", command=self.view_details, state="disabled")
        self.view_details_button.pack(side='right')
        # --- END NEW ---

        ttk.Label(self, text="Recent Activities", font=('Helvetica', 14, 'bold')).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("ID", "Date", "Car Number", "Owner", "Cost"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=40)
        self.tree.heading("Date", text="Date")
        self.tree.heading("Car Number", text="Car Number")
        self.tree.heading("Owner", text="Owner")
        self.tree.heading("Cost", text="Total Cost")
        self.tree.pack(fill="both", expand=True)

        # --- NEW: Bind selection event ---
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)
        
        self.refresh_records_display()

    def on_record_select(self, event):
        """Called when a user selects a row in the treeview."""
        selected_items = self.tree.selection()
        if selected_items:
            # If a row is selected, enable the button and store the ID
            self.view_details_button['state'] = 'normal'
            selected_item = selected_items[0]
            self.selected_record_id = self.tree.item(selected_item)['values'][0]
        else:
            # If nothing is selected, disable the button
            self.view_details_button['state'] = 'disabled'
            self.selected_record_id = None
            
    def view_details(self):
        """Calls the controller to show the details window."""
        if self.selected_record_id:
            self.controller.show_record_details(self.selected_record_id)

    def create_buttons(self, parent_frame): pass

    def refresh_records_display(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        records = self.controller.get_all_car_records()
        for record in records:
            formatted_date = record.record_date.strftime("%Y-%m-%d %H:%M")
            self.tree.insert("", "end", values=(record.id, formatted_date, record.car_number, record.owner_name, f"₹{record.total_cost:.2f}"))
        # After refreshing, clear selection and disable button
        self.tree.selection_remove(self.tree.selection())
        self.on_record_select(None)

# --- (Dashboards are unchanged but will inherit the new button logic) ---
class AdminDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add New Record", command=self.controller.show_add_record_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Decor Items", command=self.controller.show_manage_items_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Users", command=self.controller.show_manage_users_window).pack(side='left', padx=5)

class StdUserDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add New Record", command=self.controller.show_add_record_window).pack(side='left', padx=5)

# --- NEW: Details Window Class ---
class RecordDetailsWindow(tk.Toplevel):
    def __init__(self, parent, record_info, item_list):
        super().__init__(parent)
        self.title("Record Details")
        self.geometry("500x400")
        self.transient(parent)
        self.grab_set()

        # Display main record info
        info_frame = ttk.LabelFrame(self, text="Summary")
        info_frame.pack(padx=10, pady=10, fill='x')
        ttk.Label(info_frame, text=f"Car Number: {record_info.car_number}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Owner: {record_info.owner_name}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Date: {record_info.record_date.strftime('%Y-%m-%d %H:%M')}").pack(anchor='w')
        ttk.Label(info_frame, text=f"Total Cost: ₹{record_info.total_cost:.2f}").pack(anchor='w')

        # Display itemized list
        items_frame = ttk.LabelFrame(self, text="Items Used")
        items_frame.pack(padx=10, pady=5, fill='both', expand=True)
        
        tree = ttk.Treeview(items_frame, columns=("Item", "Qty", "Price", "Subtotal"), show="headings")
        tree.heading("Item", text="Item Name")
        tree.heading("Qty", text="Quantity"); tree.column("Qty", width=80)
        tree.heading("Price", text="Unit Price"); tree.column("Price", width=100)
        tree.heading("Subtotal", text="Subtotal"); tree.column("Subtotal", width=100)
        tree.pack(fill='both', expand=True)

        for item in item_list:
            subtotal = item.quantity * item.decor_item.price
            tree.insert("", "end", values=(
                item.decor_item.name,
                item.quantity,
                f"₹{item.decor_item.price:.2f}",
                f"₹{subtotal:.2f}"
            ))
            
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

        
class AddRecordWindow(tk.Toplevel):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.title("Add New Car Record")
        self.geometry("600x500")
        self.transient(parent)
        self.grab_set()
        details_frame = ttk.LabelFrame(self, text="Car Details")
        details_frame.pack(padx=10, pady=10, fill='x')
        ttk.Label(details_frame, text="Car Number:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.car_number_entry = ttk.Entry(details_frame)
        self.car_number_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(details_frame, text="Owner Name:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.owner_name_entry = ttk.Entry(details_frame)
        self.owner_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        items_frame = ttk.LabelFrame(self, text="Decor Items")
        items_frame.pack(padx=10, pady=10, fill='both', expand=True)
        available_frame = ttk.Frame(items_frame)
        available_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(available_frame, text="Available Items").pack()
        self.available_items_list = tk.Listbox(available_frame)
        self.available_items_list.pack(fill='both', expand=True)
        self.populate_available_items()
        buttons_frame = ttk.Frame(items_frame)
        buttons_frame.pack(side='left', fill='y', padx=5)
        ttk.Button(buttons_frame, text=">>", command=self.add_item).pack(pady=10)
        ttk.Button(buttons_frame, text="<<", command=self.remove_item).pack(pady=10)
        selected_frame = ttk.Frame(items_frame)
        selected_frame.pack(side='left', fill='both', expand=True, padx=5)
        ttk.Label(selected_frame, text="Selected Items (Item - Qty)").pack()
        self.selected_items_tree = ttk.Treeview(selected_frame, columns=("Name", "Qty", "Price"), show="headings")
        self.selected_items_tree.heading("Name", text="Name"); self.selected_items_tree.heading("Qty", text="Qty"); self.selected_items_tree.heading("Price", text="Price")
        self.selected_items_tree.column("Qty", width=50, anchor='center'); self.selected_items_tree.column("Price", width=80, anchor='e')
        self.selected_items_tree.pack(fill='both', expand=True)
        self.selected_items = {}
        ttk.Button(self, text="Save Record", command=self.save_record).pack(pady=10)

    def populate_available_items(self):
        items = self.controller.get_all_decor_items()
        for item in items: self.available_items_list.insert('end', f"{item.name} - ₹{item.price:.2f}")

    def add_item(self):
        selected_indices = self.available_items_list.curselection()
        if not selected_indices: return
        item_name = self.available_items_list.get(selected_indices[0]).split(' - ')[0]
        if item_name in self.selected_items: self.selected_items[item_name]['qty'] += 1
        else:
            item_obj = self.controller.get_decor_item_by_name(item_name)
            self.selected_items[item_name] = {'id': item_obj.id, 'price': item_obj.price, 'qty': 1}
        self.update_selected_tree()

    def remove_item(self):
        selected_in_tree = self.selected_items_tree.focus()
        if not selected_in_tree: return
        item_name = self.selected_items_tree.item(selected_in_tree)['values'][0]
        if item_name in self.selected_items:
            self.selected_items[item_name]['qty'] -= 1
            if self.selected_items[item_name]['qty'] == 0: del self.selected_items[item_name]
        self.update_selected_tree()

    def update_selected_tree(self):
        for item in self.selected_items_tree.get_children(): self.selected_items_tree.delete(item)
        for name, data in self.selected_items.items(): self.selected_items_tree.insert("", "end", values=(name, data['qty'], f"₹{data['price']:.2f}"))

    def save_record(self):
        car_number = self.car_number_entry.get()
        owner_name = self.owner_name_entry.get()
        if not car_number or not self.selected_items:
            messagebox.showerror("Error", "Car Number and at least one decor item are required.")
            return
        record_data = {'car_number': car_number, 'owner_name': owner_name, 'items': self.selected_items}
        self.controller.save_car_record(record_data)
        self.destroy()