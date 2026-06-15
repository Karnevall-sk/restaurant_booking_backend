import factory

from .models import User

class UserFactory(factory.django.DjangoModelFactory):

    class Meta:
        model = User

    phone = factory.Sequence(
        lambda n: f"+7700{n:07d}"
    )

    name = factory.Faker("name")

    email = factory.Faker("email")

    role = "customer"

    is_active = True
    is_verified = True

    password = factory.PostGenerationMethodCall(
        "set_password",
        "password"
    )