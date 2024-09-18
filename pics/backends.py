# yourapp/backends.py
from django.contrib.auth.backends import BaseBackend
from .models import Customers

class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None):
        try:
            user = Customers.objects.get(email=email)
            if user.check_password(password):
                return user
        except Customers.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Customers.objects.get(pk=user_id)
        except Customers.DoesNotExist:
            return None
