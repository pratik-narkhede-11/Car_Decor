from tkinter import messagebox
# Import view classes to prevent circular import issues
from view import LoginWindow, AddRecordWindow
from model import Session, User, DecorItem, CarRecord, RecordItemLink

class Controller:
    def __init__(self, model, view):
        self.model = model
        self.view = view
        self.session = self.model.Session()
        self.logged_in_user_role = None

    def start(self):
        print("DEBUG: Controller.start() called.")
        print("DEBUG: Creating LoginWindow...")
        login_win = LoginWindow(self.view, self)
        print("DEBUG: LoginWindow created. Calling wait_window()...")
        
        # The program will PAUSE here until the login_win is destroyed
        login_win.wait_window()
        print("DEBUG: wait_window() finished.")

        if self.logged_in_user_role:
            print("DEBUG: Login successful. Showing dashboard...")
            self.view.show_dashboard(self.logged_in_user_role)
            print("DEBUG: Starting mainloop()...")
            self.view.mainloop()
        else:
            print("DEBUG: Login cancelled or failed. Exiting.")

    def handle_login(self, username, password, login_window):
        user = self.session.query(User).filter_by(username=username).first()
        if user and user.check_password(password):
            print("DEBUG: Correct credentials provided.")
            self.logged_in_user_role = user.role
            login_window.destroy()
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.", parent=login_window)

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