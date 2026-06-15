from users.factories import UserFactory

def seed_users():

    UserFactory(
        phone="+77050000000",
        role="admin",
        is_staff=True,
        is_superuser=True,
        password="admin"
    )

    for _ in range(50):
        UserFactory(
            role="customer"
        )

    for _ in range(5):
        UserFactory(
            role="manager",
            is_staff=True
        )
