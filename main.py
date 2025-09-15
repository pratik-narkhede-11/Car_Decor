import model
import view
import controller

if __name__ == "__main__":
    # 1. Initialize the Model (creates DB and default user if needed)
    model.init_db()
    
    # 2. Initialize the Controller and View
    app_controller = controller.Controller(model, None)
    app_view = view.MainAppView(app_controller)
    app_controller.view = app_view # Give the controller a reference to the view

    # 3. Start the application
    app_controller.start()