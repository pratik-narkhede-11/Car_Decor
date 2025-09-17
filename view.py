import tkinter as tk
from tkinter import ttk, messagebox, font
from ttkthemes import ThemedTk
from PIL import Image, ImageTk
import os

# --- Constants for Styling ---
COLOR_DARK_BG = "#2E2E2E"
COLOR_FRAME_BG = "#3C3C3C"
COLOR_TEXT = "#EAEAEA"
COLOR_ACCENT = "#00AEEF" # A vibrant blue for highlights
COLOR_DANGER = "#DC3545"
FONT_TITLE = ("Helvetica", 18, "bold")
FONT_HEADING = ("Helvetica", 12, "bold")
FONT_BODY = ("Helvetica", 10)
FONT_BUTTON = ("Helvetica", 10, "bold")

# --- Icon Loader Utility ---
ICON_CACHE = {}
def get_icon(name, size=(16, 16)):
    """Loads an icon from the 'icons' folder and caches it."""
    if name in ICON_CACHE:
        return ICON_CACHE[name]
    try:
        path = os.path.join("icons", f"{name}.png")
        image = Image.open(path).resize(size, Image.Resampling.LANCZOS)
        photo_image = ImageTk.PhotoImage(image)
        ICON_CACHE[name] = photo_image
        return photo_image
    except FileNotFoundError:
        print(f"Warning: Icon '{name}.png' not found in 'icons' folder.")
        return None

# --- Main Application Window ---
class MainAppView(ThemedTk):
    def __init__(self, controller):
        super().__init__()
        self.set_theme("equilux")
        self.controller = controller
        self.title("Car Decor Shop Manager")
        self.dashboard = None
        self._setup_styles()
        # Hide window initially by moving it off-screen, as requested
        self.geometry("400x250+50000+50000") 

    def _setup_styles(self):
        style = ttk.Style()
        self.configure(background=COLOR_DARK_BG)
        style.configure(".", background=COLOR_DARK_BG, foreground=COLOR_TEXT, font=FONT_BODY)
        style.configure("TLabel", font=FONT_BODY)
        style.configure("TButton", font=FONT_BUTTON, padding=6)
        style.map("TButton", background=[('active', COLOR_ACCENT)], foreground=[('active', 'white')])
        style.configure("Treeview", rowheight=25, fieldbackground=COLOR_FRAME_BG)
        style.configure("Treeview.Heading", font=FONT_HEADING, padding=5)
        style.map("Treeview.Heading", background=[('active', COLOR_FRAME_BG)])
        style.configure("Accent.TButton", background=COLOR_ACCENT, foreground="white")
        style.map("Accent.TButton", background=[('active', "#007aac")])
        style.configure("Delete.TButton", background=COLOR_DANGER, foreground="white")
        style.map("Delete.TButton", background=[('active', "#a82a37")])
        style.map("TEntry", fieldbackground=[('focus', COLOR_FRAME_BG)], foreground=[('focus', COLOR_TEXT)])
        style.map("TCombobox", fieldbackground=[('readonly', COLOR_FRAME_BG)], foreground=[('readonly', COLOR_TEXT)])
        style.configure("TLabelFrame", background=COLOR_FRAME_BG)
        style.configure("TLabelFrame.Label", font=FONT_HEADING, foreground=COLOR_ACCENT, background=COLOR_FRAME_BG)

    def show_dashboard(self, user_role):
        if self.dashboard: self.dashboard.destroy()
        if user_role == 'admin':
            self.dashboard = AdminDashboard(self, self.controller)
        else:
            self.dashboard = StdUserDashboard(self, self.controller)
        self.center_on_screen()
        # This makes the window visible after it was moved off-screen
        self.deiconify()

    def center_on_screen(self):
        self.update_idletasks()
        width, height = self.winfo_width(), self.winfo_height()
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (screen_w // 2) - (width // 2)
        y = (screen_h // 2) - (height // 2)
        self.geometry(f'{width}x{height}+{x}+{y}')

# --- Base Toplevel Window ---
class BaseToplevel(tk.Toplevel):
    def __init__(self, parent, title, geometry="800x500"):
        super().__init__(parent)
        self.title(title)
        self.configure(background=COLOR_DARK_BG)
        self.transient(parent)
        self.grab_set()
        w, h = map(int, geometry.split('x'))
        screen_w, screen_h = self.winfo_screenwidth(), self.winfo_screenheight()
        x = (screen_w // 2) - (w // 2)
        y = (screen_h // 2) - (h // 2)
        self.geometry(f"{geometry}+{x}+{y}")
        self.protocol("WM_DELETE_WINDOW", self.destroy)

# --- Application Windows ---
class LoginWindow(BaseToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent, "Login", "400x250")
        self.controller = controller
        main_frame = ttk.Frame(self, padding=(20, 10))
        main_frame.pack(expand=True, fill="both")
        ttk.Label(main_frame, text="Welcome Back", font=FONT_TITLE, foreground=COLOR_ACCENT).pack(pady=(0, 20))
        ttk.Label(main_frame, text="Username").pack(fill="x", padx=20)
        self.username_entry = ttk.Entry(main_frame, width=30)
        self.username_entry.pack(fill="x", padx=20, pady=(0, 10))
        ttk.Label(main_frame, text="Password").pack(fill="x", padx=20)
        self.password_entry = ttk.Entry(main_frame, show="*", width=30)
        self.password_entry.pack(fill="x", padx=20, pady=(0, 20))
        ttk.Button(main_frame, text="Login", command=self.login, style="Accent.TButton").pack(pady=10)
        self.username_entry.focus()
        self.bind("<Return>", lambda e: self.login())

    def login(self):
        self.controller.handle_login(self.username_entry.get(), self.password_entry.get(), self)

class DashboardFrame(ttk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent, padding=10)
        self.controller = controller
        self.pack(fill="both", expand=True)
        parent.geometry("900x600")
        self.selected_record_id = None
        self.create_ui()

    def create_ui(self):
        top_frame = ttk.Frame(self)
        top_frame.pack(fill='x', pady=(0, 10))
        action_buttons_frame = ttk.Frame(top_frame)
        action_buttons_frame.pack(side='left')
        self.create_buttons(action_buttons_frame)
        search_details_frame = ttk.Frame(top_frame)
        search_details_frame.pack(side='right')
        self.search_entry = ttk.Entry(search_details_frame, width=25, font=FONT_BODY)
        self.search_entry.insert(0, "Search by Car Plate...")
        self.search_entry.bind("<FocusIn>", lambda e: e.widget.delete(0, 'end'))
        self.search_entry.bind("<Return>", lambda e: self.perform_search())
        self.search_entry.pack(side='left', padx=5, ipady=4)
        ttk.Button(search_details_frame, image=get_icon('search'), command=self.perform_search).pack(side='left')
        ttk.Button(search_details_frame, image=get_icon('clear'), command=self.clear_search).pack(side='left', padx=(0, 10))
        self.view_details_button = ttk.Button(search_details_frame, text="View Details", image=get_icon('details'), compound="left", command=self.view_details, state="disabled")
        self.view_details_button.pack(side='left')
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True)
        ttk.Label(tree_frame, text="Recent Activities", font=FONT_TITLE, foreground=COLOR_ACCENT).pack(pady=(5, 10))
        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side='right', fill='y')
        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Date", "Car Number", "Owner", "Cost"), show='headings', yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.tree.yview)
        self.tree.heading("ID", text="ID"); self.tree.column("ID", width=50, anchor='center')
        self.tree.heading("Date", text="Date"); self.tree.column("Date", width=150)
        self.tree.heading("Car Number", text="Car Number"); self.tree.column("Car Number", width=150)
        self.tree.heading("Owner", text="Owner"); self.tree.column("Owner", width=150)
        self.tree.heading("Cost", text="Total Cost"); self.tree.column("Cost", width=120, anchor='e')
        self.tree.pack(fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", self.on_record_select)
        self.refresh_records_display()

    def perform_search(self):
        search_term = self.search_entry.get()
        if search_term and search_term != "Search by Car Plate...":
            self.controller.handle_search_by_car_number(search_term)

    def clear_search(self):
        self.search_entry.delete(0, 'end')
        self.search_entry.insert(0, "Search by Car Plate...")
        self.controller.handle_clear_search()
        self.master.focus()

    def on_record_select(self, event=None):
        if self.tree.selection():
            self.view_details_button['state'] = 'normal'
            self.selected_record_id = self.tree.item(self.tree.selection()[0])['values'][0]
        else:
            self.view_details_button['state'] = 'disabled'
            self.selected_record_id = None

    def view_details(self):
        if self.selected_record_id:
            self.controller.show_record_details(self.selected_record_id)

    def create_buttons(self, parent_frame): pass

    def refresh_records_display(self, records=None):
        self.tree.delete(*self.tree.get_children())
        record_list = records if records is not None else self.controller.get_all_car_records()
        for record in record_list:
            formatted_date = record.record_date.strftime("%Y-%m-%d %H:%M")
            self.tree.insert("", "end", values=(record.id, formatted_date, record.car_number, record.owner_name, f"₹{record.total_cost:.2f}"))
        self.on_record_select()

class AdminDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add Record", image=get_icon('add'), compound="left", command=self.controller.show_add_record_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Items", image=get_icon('items'), compound="left", command=self.controller.show_manage_items_window).pack(side='left', padx=5)
        ttk.Button(parent_frame, text="Manage Users", image=get_icon('users'), compound="left", command=self.controller.show_manage_users_window).pack(side='left', padx=5)
        export_button = ttk.Menubutton(parent_frame, text="Export", image=get_icon('export'), compound="left")
        export_menu = tk.Menu(export_button, tearoff=0, background=COLOR_FRAME_BG, foreground=COLOR_TEXT)
        export_button["menu"] = export_menu
        export_menu.add_command(label="Export All Users", command=self.controller.export_users_to_csv)
        export_menu.add_command(label="Export All Records", command=self.controller.export_all_records_to_csv)
        export_button.pack(side='left', padx=5)

class StdUserDashboard(DashboardFrame):
    def create_buttons(self, parent_frame):
        ttk.Button(parent_frame, text="Add New Record", image=get_icon('add'), compound="left", command=self.controller.show_add_record_window).pack(side='left', padx=5)

class RecordDetailsWindow(BaseToplevel):
    def __init__(self, parent, record_info, item_list):
        super().__init__(parent, f"Details for Car: {record_info.car_number}", "700x500")
        info_frame = ttk.LabelFrame(self, text="Summary", padding=15)
        info_frame.pack(padx=10, pady=10, fill='x')
        info_frame.columnconfigure((1, 3), weight=1)
        ttk.Label(info_frame, text="Car Number:", font=FONT_HEADING).grid(row=0, column=0, sticky='w', padx=5)
        ttk.Label(info_frame, text=record_info.car_number).grid(row=0, column=1, sticky='w')
        ttk.Label(info_frame, text="Owner:", font=FONT_HEADING).grid(row=1, column=0, sticky='w', padx=5)
        ttk.Label(info_frame, text=record_info.owner_name).grid(row=1, column=1, sticky='w')
        ttk.Label(info_frame, text="Date:", font=FONT_HEADING).grid(row=0, column=2, sticky='w', padx=5)
        ttk.Label(info_frame, text=record_info.record_date.strftime('%Y-%m-%d %H:%M')).grid(row=0, column=3, sticky='w')
        ttk.Label(info_frame, text="Total Cost:", font=FONT_HEADING).grid(row=1, column=2, sticky='w', padx=5)
        ttk.Label(info_frame, text=f"₹{record_info.total_cost:.2f}", foreground=COLOR_ACCENT, font=FONT_HEADING).grid(row=1, column=3, sticky='w')
        items_frame = ttk.LabelFrame(self, text="Items Used", padding=10)
        items_frame.pack(padx=10, pady=5, fill='both', expand=True)
        tree = ttk.Treeview(items_frame, columns=("Item", "Qty", "Price", "Subtotal"), show="headings")
        tree.heading("Item", text="Item Name")
        tree.heading("Qty", text="Quantity"); tree.column("Qty", width=80, anchor='center')
        tree.heading("Price", text="Unit Price"); tree.column("Price", width=120, anchor='e')
        tree.heading("Subtotal", text="Subtotal"); tree.column("Subtotal", width=120, anchor='e')
        tree.pack(fill='both', expand=True)
        for item in item_list:
            subtotal = item.quantity * item.decor_item.price
            tree.insert("", "end", values=(item.decor_item.name, item.quantity, f"₹{item.decor_item.price:.2f}", f"₹{subtotal:.2f}"))
        ttk.Button(self, text="Close", command=self.destroy).pack(pady=10)

class AddRecordWindow(BaseToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent, "Add New Car Record", "850x550")
        self.controller = controller
        self.selected_items = {}
        self.create_widgets()

    def create_widgets(self):
        details_frame = ttk.LabelFrame(self, text="Car & Owner Details", padding=15)
        details_frame.pack(padx=10, pady=10, fill='x')
        details_frame.columnconfigure(1, weight=1)
        ttk.Label(details_frame, text="Car Plate Number:", font=FONT_HEADING).grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.car_number_entry = ttk.Entry(details_frame)
        self.car_number_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(details_frame, text="Owner Name:", font=FONT_HEADING).grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.owner_name_entry = ttk.Entry(details_frame)
        self.owner_name_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        items_frame = ttk.LabelFrame(self, text="Select Decor Items", padding=10)
        items_frame.pack(padx=10, pady=10, fill='both', expand=True)
        items_frame.columnconfigure((0, 2), weight=1)
        items_frame.rowconfigure(1, weight=1)
        ttk.Label(items_frame, text="Available Items").grid(row=0, column=0)
        self.available_items_list = tk.Listbox(items_frame, bg=COLOR_FRAME_BG, fg=COLOR_TEXT, selectbackground=COLOR_ACCENT, borderwidth=0, highlightthickness=0)
        self.available_items_list.grid(row=1, column=0, sticky='nsew', padx=(0,5))
        self.populate_available_items()
        buttons_frame = ttk.Frame(items_frame)
        buttons_frame.grid(row=1, column=1, padx=10)
        ttk.Button(buttons_frame, text=">>", command=self.add_item).pack(pady=5)
        ttk.Button(buttons_frame, text="<<", command=self.remove_item).pack(pady=5)
        ttk.Label(items_frame, text="Selected Items").grid(row=0, column=2)
        self.selected_items_tree = ttk.Treeview(items_frame, columns=("Name", "Qty", "Price"), show="headings")
        self.selected_items_tree.heading("Name", text="Name")
        self.selected_items_tree.heading("Qty", text="Qty"); self.selected_items_tree.column("Qty", width=50, anchor='center')
        self.selected_items_tree.heading("Price", text="Price"); self.selected_items_tree.column("Price", width=80, anchor='e')
        self.selected_items_tree.grid(row=1, column=2, sticky='nsew', padx=(5,0))
        save_frame = ttk.Frame(self)
        save_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(save_frame, text="Save Record", style="Accent.TButton", command=self.save_record).pack()

    def populate_available_items(self):
        for item in self.controller.get_all_decor_items():
            self.available_items_list.insert('end', f"{item.name} - ₹{item.price:.2f}")

    def add_item(self):
        if not self.available_items_list.curselection(): return
        item_name = self.available_items_list.get(self.available_items_list.curselection()[0]).split(' - ')[0]
        if item_name in self.selected_items:
            self.selected_items[item_name]['qty'] += 1
        else:
            item_obj = self.controller.get_decor_item_by_name(item_name)
            self.selected_items[item_name] = {'id': item_obj.id, 'price': item_obj.price, 'qty': 1}
        self.update_selected_tree()

    def remove_item(self):
        if not self.selected_items_tree.focus(): return
        item_name = self.selected_items_tree.item(self.selected_items_tree.focus())['values'][0]
        if item_name in self.selected_items:
            self.selected_items[item_name]['qty'] -= 1
            if self.selected_items[item_name]['qty'] == 0: del self.selected_items[item_name]
        self.update_selected_tree()

    def update_selected_tree(self):
        self.selected_items_tree.delete(*self.selected_items_tree.get_children())
        for name, data in self.selected_items.items():
            self.selected_items_tree.insert("", "end", values=(name, data['qty'], f"₹{data['price']:.2f}"))

    def save_record(self):
        car_number, owner_name = self.car_number_entry.get(), self.owner_name_entry.get()
        if not car_number or not self.selected_items:
            messagebox.showerror("Error", "Car Number and at least one item are required.", parent=self)
            return
        self.controller.save_car_record({'car_number': car_number, 'owner_name': owner_name, 'items': self.selected_items})
        self.destroy()

class ManageItemsWindow(BaseToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent, "Manage Decor Items")
        self.controller = controller
        self.create_widgets()
        self.populate_items_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=3); main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        list_frame = ttk.LabelFrame(main_frame, text="Available Items", padding=10)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.item_tree = ttk.Treeview(list_frame, columns=("ID", "Name", "Price"), show="headings")
        self.item_tree.heading("ID", text="ID"); self.item_tree.column("ID", width=40)
        self.item_tree.heading("Name", text="Item Name")
        self.item_tree.heading("Price", text="Price"); self.item_tree.column("Price", width=100, anchor='e')
        self.item_tree.pack(fill='both', expand=True)
        self.item_tree.bind("<<TreeviewSelect>>", self.on_item_select)
        form_frame = ttk.LabelFrame(main_frame, text="Item Details", padding=15)
        form_frame.grid(row=0, column=1, sticky='nsew')
        form_frame.columnconfigure(1, weight=1)
        ttk.Label(form_frame, text="Name:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(form_frame, text="Price:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.price_entry = ttk.Entry(form_frame)
        self.price_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=2, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(button_frame, text="Add New", image=get_icon('add'), compound="left", command=self.add_item).pack(fill='x', pady=2)
        self.update_button = ttk.Button(button_frame, text="Update Selected", image=get_icon('edit'), compound="left", command=self.update_item, state="disabled")
        self.update_button.pack(fill='x', pady=2)
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", image=get_icon('delete'), compound="left", style="Delete.TButton", command=self.delete_item, state="disabled")
        self.delete_button.pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Clear Form", image=get_icon('clear'), compound="left", command=self.clear_form).pack(fill='x', pady=(10, 2))

    def populate_items_list(self):
        self.item_tree.delete(*self.item_tree.get_children())
        for item in self.controller.get_all_decor_items():
            self.item_tree.insert("", "end", values=(item.id, item.name, f"₹{item.price:.2f}"))
        self.clear_form()

    def on_item_select(self, event=None):
        if self.item_tree.selection():
            item_values = self.item_tree.item(self.item_tree.selection()[0], 'values')
            self.name_entry.delete(0, 'end'); self.name_entry.insert(0, item_values[1])
            self.price_entry.delete(0, 'end'); self.price_entry.insert(0, str(item_values[2]).replace('₹', ''))
            self.update_button['state'] = 'normal'; self.delete_button['state'] = 'normal'
        else:
            self.update_button['state'] = 'disabled'; self.delete_button['state'] = 'disabled'

    def clear_form(self):
        self.name_entry.delete(0, 'end'); self.price_entry.delete(0, 'end')
        if self.item_tree.selection(): self.item_tree.selection_remove(self.item_tree.selection()[0])
        self.on_item_select()

    def add_item(self):
        if self.controller.add_decor_item(self.name_entry.get(), self.price_entry.get(), self):
            self.populate_items_list()

    def update_item(self):
        if not self.item_tree.selection(): return
        item_id = self.item_tree.item(self.item_tree.selection()[0], 'values')[0]
        if self.controller.update_decor_item(item_id, self.name_entry.get(), self.price_entry.get(), self):
            self.populate_items_list()

    def delete_item(self):
        if not self.item_tree.selection(): return
        item_id, item_name = self.item_tree.item(self.item_tree.selection()[0], 'values')[0:2]
        if messagebox.askyesno("Confirm Delete", f"Delete '{item_name}'?", parent=self):
            if self.controller.delete_decor_item(item_id, self): self.populate_items_list()

class ManageUsersWindow(BaseToplevel):
    def __init__(self, parent, controller):
        super().__init__(parent, "Manage Users")
        self.controller = controller
        self.create_widgets()
        self.populate_users_list()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding=10)
        main_frame.pack(fill='both', expand=True)
        main_frame.columnconfigure(0, weight=3); main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)
        list_frame = ttk.LabelFrame(main_frame, text="Application Users", padding=10)
        list_frame.grid(row=0, column=0, sticky='nsew', padx=(0, 10))
        self.user_tree = ttk.Treeview(list_frame, columns=("ID", "Username", "Role"), show="headings")
        self.user_tree.heading("ID", text="ID"); self.user_tree.column("ID", width=40)
        self.user_tree.heading("Username", text="Username")
        self.user_tree.heading("Role", text="Role"); self.user_tree.column("Role", width=80)
        self.user_tree.pack(fill='both', expand=True)
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)
        form_frame = ttk.LabelFrame(main_frame, text="User Details", padding=15)
        form_frame.grid(row=0, column=1, sticky='nsew')
        form_frame.columnconfigure(1, weight=1)
        ttk.Label(form_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky='w')
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(form_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky='w')
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5, sticky='ew')
        ttk.Label(form_frame, text="(Leave blank to keep current password)", font=(FONT_BODY[0], 8)).grid(row=2, column=1, sticky='w', padx=5)
        ttk.Label(form_frame, text="Role:").grid(row=3, column=0, padx=5, pady=10, sticky='w')
        self.role_combobox = ttk.Combobox(form_frame, values=['std', 'admin'], state='readonly')
        self.role_combobox.grid(row=3, column=1, padx=5, pady=10, sticky='ew')
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=4, column=0, columnspan=2, pady=(20, 0))
        ttk.Button(button_frame, text="Add New User", image=get_icon('add'), compound="left", command=self.add_user).pack(fill='x', pady=2)
        self.update_button = ttk.Button(button_frame, text="Update Selected", image=get_icon('edit'), compound="left", command=self.update_user, state="disabled")
        self.update_button.pack(fill='x', pady=2)
        self.delete_button = ttk.Button(button_frame, text="Delete Selected", image=get_icon('delete'), compound="left", style="Delete.TButton", command=self.delete_user, state="disabled")
        self.delete_button.pack(fill='x', pady=2)
        ttk.Button(button_frame, text="Clear Form", image=get_icon('clear'), compound="left", command=self.clear_form).pack(fill='x', pady=(10, 2))

    def populate_users_list(self):
        self.user_tree.delete(*self.user_tree.get_children())
        for user in self.controller.get_all_users():
            self.user_tree.insert("", "end", values=(user.id, user.username, user.role))
        self.clear_form()

    def on_user_select(self, event=None):
        if self.user_tree.selection():
            user_values = self.user_tree.item(self.user_tree.selection()[0], 'values')
            self.username_entry.delete(0, 'end'); self.username_entry.insert(0, user_values[1])
            self.role_combobox.set(user_values[2])
            self.password_entry.delete(0, 'end')
            self.update_button['state'] = 'normal'; self.delete_button['state'] = 'normal'
        else:
            self.update_button['state'] = 'disabled'; self.delete_button['state'] = 'disabled'

    def clear_form(self):
        self.username_entry.delete(0, 'end'); self.password_entry.delete(0, 'end')
        self.role_combobox.set('')
        if self.user_tree.selection(): self.user_tree.selection_remove(self.user_tree.selection()[0])
        self.on_user_select()

    def add_user(self):
        if self.controller.add_user(self.username_entry.get(), self.password_entry.get(), self.role_combobox.get(), self):
            self.populate_users_list()

    def update_user(self):
        if not self.user_tree.selection(): return
        user_id = self.user_tree.item(self.user_tree.selection()[0], 'values')[0]
        if self.controller.update_user(user_id, self.username_entry.get(), self.password_entry.get(), self.role_combobox.get(), self):
            self.populate_users_list()

    def delete_user(self):
        if not self.user_tree.selection(): return
        user_id, username = self.user_tree.item(self.user_tree.selection()[0], 'values')[0:2]
        if messagebox.askyesno("Confirm Delete", f"Delete user '{username}'?", parent=self):
            if self.controller.delete_user(user_id, self): self.populate_users_list()