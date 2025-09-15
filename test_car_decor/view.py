import tkinter as tk
from tkinter import ttk, messagebox

class MainAppView(tk.Tk):
    def __init__(self, controller):
        print("DEBUG: MainAppView.__init__ started.")
        super().__init__()
        self.controller = controller
        self.title("Car Decor Shop Manager")
        self.dashboard = None
        
        # --- SOLUTION ---
        # Instead of self.withdraw(), we move the window off-screen.
        # This keeps it active for the Toplevel, but invisible to the user.
        self.geometry("400x250+5000+5000") 
        print("DEBUG: MainAppView.__init__ finished.")

    def show_dashboard(self, user_role):
        """Builds the dashboard and then centers the main window."""
        # First, build the dashboard content
        if user_role == 'admin':
            self.dashboard = AdminDashboard(self, self.controller)
        else:
            self.dashboard = StdUserDashboard(self, self.controller)
            
        # Now, make the window visible by moving it to the center of the screen
        self.deiconify() # This is needed in case the window was minimized
        self.center_on_screen()

    def center_on_screen(self):
        """Centers the main window on the user's screen."""
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
        print("DEBUG: LoginWindow.__init__ started.")
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
        print("DEBUG: LoginWindow.__init__ finished.")

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        self.controller.handle_login(username, password, self)

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller
        self.pack(fill="both", expand=True, padx=10, pady=10)
        parent.geometry("800x600")
        self.create_ui()

    def create_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', pady=5)
        self.create_buttons(top_frame)
        ttk.Label(self, text="Recent Activities", font=('Helvetica', 14, 'bold')).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("ID", "Date", "Car Number", "Owner", "Cost"), show='headings')
        self.tree.heading("ID", text="ID"); self.tree.heading("Date", text="Date")
        self.tree.heading("Car Number", text="Car Number"); self.tree.heading("Owner", text="Owner")
        self.tree.heading("Cost", text="Total Cost")
        self.tree.pack(fill="both", expand=True)
        self.refresh_records_display()

    def create_buttons(self, parent_frame): pass

    def refresh_records_display(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        records = self.controller.get_all_car_records()
        for record in records:
            formatted_date = record.record_date.strftime("%Y-%m-%d %H:%M")
            self.tree.insert("", "end", values=(record.id, formatted_date, record.car_number, record.owner_name, f"₹{record.total_cost:.2f}"))

class AdminDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add New Record", command=self.controller.show_add_record_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Decor Items", command=self.controller.show_manage_items_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Users", command=self.controller.show_manage_users_window).pack(side='left', padx=5)

class StdUserDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add New Record", command=self.controller.show_add_record_window).pack(side='left', padx=5)

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