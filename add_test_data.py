from model import Session, DecorItem, User, init_db

def add_data():
    init_db()
    session = Session()

    if session.query(DecorItem).count() == 0:
        print("Adding sample decor items...")
        session.add_all([
            DecorItem(name="Leather Seat Cover", price=8500.00),
            DecorItem(name="Floor Mat Set", price=2200.00),
            DecorItem(name="Steering Wheel Cover", price=750.00),
            DecorItem(name="Android Music System", price=12500.00)
        ])
        print("Items added.")
    else:
        print("Decor items already exist.")

    if not session.query(User).filter_by(username='testuser').first():
        print("Adding sample standard user...")
        std_user = User(username='testuser', role='std')
        std_user.set_password('test')
        session.add(std_user)
        print("Standard user 'testuser' created.")
    else:
        print("Standard user 'testuser' already exists.")

    session.commit()
    session.close()

if __name__ == "__main__":
    add_data()