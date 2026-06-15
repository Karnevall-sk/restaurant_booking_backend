from .users import seed_users
from .menu import seed_menu
from .reservations import seed_reservations
from .restaurants import seed_restaurants

def seed_all():

    print("Creating users...")
    seed_users()

    print("Creating restaurants...")
    seed_restaurants()

    print("Creating menu...")
    seed_menu()

    print("Creating reservations...")
    seed_reservations()

    print("Done.")