# controller.py
import csv
from datetime import datetime, timedelta
from tkinter import filedialog, messagebox
# UPDATED: Import the new window classes
from view import LoginWindow, AddRecordWindow, RecordDetailsWindow, DateRangeDialog, ManageItemsWindow, ManageUsersWindow
from model import Session, User, DecorItem, CarRecord, RecordItemLink
from sqlalchemy.exc import IntegrityError # For handling DB constraint errors

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
        record = self.session.query(CarRecord).filter_by(id=record_id).first()
        return record, record.items_used

    def show_record_details(self, record_id):
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

    # --- Decor Item Management (NEW) ---
    def show_manage_items_window(self):
        manage_win = ManageItemsWindow(self.view, self)
        manage_win.wait_window()
        # Refresh dashboard if needed after closing, though it's not strictly necessary for this app
        if self.view.dashboard:
            self.view.dashboard.refresh_records_display()

    def add_decor_item(self, name, price_str, parent_win):
        if not name or not price_str:
            messagebox.showerror("Input Error", "Name and price cannot be empty.", parent=parent_win)
            return False
        try:
            price = float(price_str)
            if price < 0:
                messagebox.showerror("Input Error", "Price cannot be negative.", parent=parent_win)
                return False
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a valid number.", parent=parent_win)
            return False
            
        try:
            new_item = DecorItem(name=name, price=price)
            self.session.add(new_item)
            self.session.commit()
            messagebox.showinfo("Success", f"Item '{name}' added successfully.", parent=parent_win)
            return True
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Database Error", f"An item with the name '{name}' already exists.", parent=parent_win)
            return False
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False

    def update_decor_item(self, item_id, name, price_str, parent_win):
        if not name or not price_str:
            messagebox.showerror("Input Error", "Name and price cannot be empty.", parent=parent_win)
            return False
        try:
            price = float(price_str)
        except ValueError:
            messagebox.showerror("Input Error", "Price must be a valid number.", parent=parent_win)
            return False
            
        try:
            item = self.session.query(DecorItem).filter_by(id=item_id).first()
            if item:
                item.name = name
                item.price = price
                self.session.commit()
                messagebox.showinfo("Success", "Item updated successfully.", parent=parent_win)
                return True
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Database Error", f"An item with the name '{name}' already exists.", parent=parent_win)
            return False
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False
        return False

    def delete_decor_item(self, item_id, parent_win):
        try:
            item = self.session.query(DecorItem).filter_by(id=item_id).first()
            if item:
                self.session.delete(item)
                self.session.commit()
                messagebox.showinfo("Success", "Item deleted successfully.", parent=parent_win)
                return True
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Delete Error", "Cannot delete item. It is currently used in existing records.", parent=parent_win)
            return False
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False
        return False

    # --- User Management (NEW) ---
    def show_manage_users_window(self):
        manage_win = ManageUsersWindow(self.view, self)
        manage_win.wait_window()

    def get_all_users(self):
        return self.session.query(User).order_by(User.username).all()

    def add_user(self, username, password, role, parent_win):
        if not all([username, password, role]):
            messagebox.showerror("Input Error", "Username, password, and role are required.", parent=parent_win)
            return False
        try:
            new_user = User(username=username, role=role)
            new_user.set_password(password)
            self.session.add(new_user)
            self.session.commit()
            messagebox.showinfo("Success", f"User '{username}' created successfully.", parent=parent_win)
            return True
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Database Error", f"Username '{username}' already exists.", parent=parent_win)
            return False
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False

    def update_user(self, user_id, username, password, role, parent_win):
        if not all([username, role]):
            messagebox.showerror("Input Error", "Username and role are required.", parent=parent_win)
            return False
            
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            if user:
                user.username = username
                user.role = role
                if password: # Only update password if a new one is provided
                    user.set_password(password)
                self.session.commit()
                messagebox.showinfo("Success", "User updated successfully.", parent=parent_win)
                return True
        except IntegrityError:
            self.session.rollback()
            messagebox.showerror("Database Error", f"Username '{username}' already exists.", parent=parent_win)
            return False
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False
        return False

    def delete_user(self, user_id, parent_win):
        # Safety Check: Prevent deleting the last admin user
        if self.session.query(User).filter_by(id=user_id).first().role == 'admin':
            admin_count = self.session.query(User).filter_by(role='admin').count()
            if admin_count <= 1:
                messagebox.showwarning("Delete Error", "Cannot delete the last remaining admin user.", parent=parent_win)
                return False
        try:
            user = self.session.query(User).filter_by(id=user_id).first()
            if user:
                self.session.delete(user)
                self.session.commit()
                messagebox.showinfo("Success", "User deleted successfully.", parent=parent_win)
                return True
        except Exception as e:
            self.session.rollback()
            messagebox.showerror("Error", f"An unexpected error occurred: {e}", parent=parent_win)
            return False
        return False


    # --- Other Methods ---
    def get_all_decor_items(self):
        return self.session.query(DecorItem).order_by(DecorItem.name).all()

    def get_decor_item_by_name(self, name):
        return self.session.query(DecorItem).filter_by(name=name).first()

    def get_today_date_str(self):
        return datetime.now().strftime('%Y-%m-%d')
        
    def export_users_to_csv(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Save User List As"
        )
        if not filepath:
            return

        try:
            users = self.session.query(User).all()
            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username', 'Role'])
                for user in users:
                    writer.writerow([user.username, user.role])
            messagebox.showinfo("Success", f"Successfully exported users to\n{filepath}")
        except Exception as e:
            messagebox.showerror("Export Error", f"An error occurred: {e}")

    def prompt_for_records_export(self):
        dialog = DateRangeDialog(self.view, self)
        dialog.wait_window()

    def export_records_to_csv(self, start_date_str, end_date_str):
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
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
            return

        try:
            records = self.session.query(CarRecord).filter(
                CarRecord.record_date >= start_date,
                CarRecord.record_date < end_date
            ).all()

            with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Record ID', 'Date', 'Car Number', 'Owner', 'Total Cost', 'Items Used'])
                for record in records:
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