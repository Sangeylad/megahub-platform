# backend/auth_core/tests/factories.py

import factory
from django.contrib.auth.hashers import make_password
from users_core.models.user import CustomUser

class UserFactory(factory.django.DjangoModelFactory):
    """Factory pour créer des utilisateurs de test"""
    
    class Meta:
        model = CustomUser
    
    username = factory.Sequence(lambda n: f"user{n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.username}@example.com")
    first_name = factory.Faker('first_name')
    last_name = factory.Faker('last_name')
    password = factory.LazyFunction(lambda: make_password('testpass123'))
    user_type = 'brand_member'
    is_active = True
    phone = factory.Faker('phone_number')
    position = factory.Faker('job')
