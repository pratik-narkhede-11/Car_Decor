import csv
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
from view import LoginWindow, AddRecordWindow, RecordDetailsWindow, DateRangeDialog
from model import Session, User, DecorItem, CarRecord, RecordItemLink

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.session = self.model.Session()
        self.logged_in_user_role = None

    def start(self):
        login_win = LoginWindow(self.view, self)
        login_win.wait_window()
        if self.logged_in_user_role:
            self.view.show_dashboard(self.logged_in_user_role)
            self.view.mainloop()

    def handle_login(self, username, password, login_window):
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            self.logged_in_user_role = user.role
            login_window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=login_window)

    # --- Record Details Methods ---
    def get_details_for_record(self, record_id):
        """Fetches a record and its associated items from the database."""
        record = self.session.query(CarRecord).filter_by(id=record_id).first()
        # The items are accessed via the 'items_used' relationship defined in the model
        return record, record.items_used

    def show_record_details(self, record_id):
        """Coordinates fetching details and showing the details window."""
        if not record_id:
            return
        
        record_info, item_list = self.get_details_for_record(record_id)
        
        if record_info:
            details_win = RecordDetailsWindow(self.view, record_info, item_list)
            details_win.wait_window()
        else:
            messagebox.showerror("Error", "Could not find details for the selected record.")

    # --- Car Record Methods ---
    def show_add_record_window(self):
        add_win = AddRecordWindow(self.view, self)
        add_win.wait_window()

    def get_all_car_records(self):
        return self.session.query(CarRecord).order_by(CarRecord.record_date.desc()).all()

    def save_car_record(self, data):
        try:
            total_cost = sum(item['price'] * item['qty'] for item in data['items'].values())
            new_record = CarRecord(
                car_number=data['car_number'],
                owner_name=data['owner_name'],
                total_cost=total_cost
            )
            self.session.add(new_record)
            self.session.flush()

            for item_data in data['items'].values():
                link = RecordItemLink(
                    car_record_id=new_record.id,
                    decor_item_id=item_data['id'],
                    quantity=item_data['qty']
                )
                self.session.add(link)

            self.session.commit()
            messagebox.showinfo("Success", "Record saved successfully.")
            if self.view.dashboard:
                self.view.dashboard.refresh_records_display()

        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Database Error", f"Could not save record: {e}")

    # --- Other Methods ---
    def get_all_decor_items(self):
        return self.session.query(DecorItem).order_by(DecorItem.name).all()

    def get_decor_item_by_name(self, name):
        return self.session.query(DecorItem).filter_by(name=name).first()

    def show_manage_items_window(self):
        messagebox.showinfo("Info", "Manage Decor Items UI not implemented yet.")

    def show_manage_users_window(self):
        messagebox.showinfo("Info", "Manage Users UI not implemented yet.")

    def get_today_date_str(self):
        """Helper method to get today's date as a string."""
        return datetime.now().strftime('%Y-%m-%d')
        
    def export_users_to_csv(self):
        """Exports all users and their roles to a CSV file."""
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save User List As"
        )
        if not filepath:
            return # User cancelled

        try:
            users = self.session.query(User).all()
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Username', 'Role'])
                # Write data
                for user in users:
                    writer.writerow([user.username, user.role])
            messagebox.showinfo("Success", f"Successfully exported users to\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")

    def prompt_for_records_export(self):
        """Opens the date range selection dialog."""
        dialog = DateRangeDialog(self.view, self)
        dialog.wait_window()

    def export_records_to_csv(self, start_date_str, end_date_str):
        """Exports car records within a given date range to a CSV file."""
        try:
            # Convert string dates to datetime objects
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
            # Add 1 day to the end date to make the range inclusive
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d') + timedelta(days=1)
        except ValueError:
            messagebox.showerror("Invalid Date", "Please enter dates in YYYY-MM-DD format.")
            return

        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save Records As"
        )
        if not filepath:
            return # User cancelled

        try:
            records = self.session.query(CarRecord).filter(
                CarRecord.record_date >= start_date,
                CarRecord.record_date < end_date
            ).all()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                # Write header
                writer.writerow(['Record ID', 'Date', 'Car Number', 'Owner', 'Total Cost', 'Items Used'])
                # Write data
                for record in records:
                    # Format the list of items into a single string
                    items_str = ", ".join(
                        f"{link.decor_item.name} (Qty: {link.quantity})"
                        for link in record.items_used
                    )
                    writer.writerow([
                        record.id,
                        record.record_date.strftime('%Y-%m-%d %H:%M'),
                        record.car_number,
                        record.owner_name,
                        record.total_cost,
                        items_str
                    ])
            messagebox.showinfo("Success", f"Successfully exported {len(records)} records to\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")