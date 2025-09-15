import model
import view
import controller

if __name__ == "__main__":
    print("DEBUG: main.py started.")
    
    # 1. Initialize the Model (creates DB and default user if needed)
    model.init_db()
    
    # 2. Initialize the Controller and View
    # NOTE: The controller and view must be linked after creation.
    print("DEBUG: Initializing components...")
    app_controller = controller.Controller(model, None)
    app_view = view.MainAppView(app_controller)
    app_controller.view = app_view # Give the controller a reference to the view
    print("DEBUG: Components initialized and linked.")

    # 3. Start the application
    print("DEBUG: Calling controller.start()...")
    app_controller.start()
    
    print("DEBUG: main.py finished.")