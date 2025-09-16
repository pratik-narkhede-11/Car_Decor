# main.py

import os
import model
import view
import controller

def main():
    """
    Sets up the application's environment, database, and MVC components, 
    and then starts the main application loop.
    """
    # --- 1. Define Application Paths ---
    # Use a persistent location in the user's home directory to store data.
    # This prevents the database from being deleted after the app closes.
    home_dir = os.path.expanduser("~")
    app_data_dir = os.path.join(home_dir, "CarDecorApp")
    database_path = os.path.join(app_data_dir, "car_decor.db")

    # --- 2. Initialize Database (Only if it doesn't exist) ---
    # This is the crucial fix: we check for the file's existence first.
    if not os.path.exists(database_path):
        print(f"Database not found. Initializing at: {database_path}")
        # Make sure the directory exists before creating the DB file
        os.makedirs(app_data_dir, exist_ok=True) 
        model.init_db()
        print("Database initialized successfully.")

    # --- 3. Set Up MVC Components ---
    # The Model is already imported and configured by this point.
    
    # Initialize the Controller, which acts as the brain of the app.
    app_controller = controller.Controller(model, None)

    # Initialize the View (the GUI), and give it a reference to the controller.
    app_view = view.MainAppView(app_controller)

    # Now, give the controller a reference to the view it will manage.
    app_controller.view = app_view 

    # --- 4. Start the Application ---
    # The controller takes over and runs the application.
    print("Starting application...")
    app_controller.start()


if __name__ == "__main__":
    main()