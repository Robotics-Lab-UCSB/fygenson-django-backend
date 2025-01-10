from django.db import models
from django.conf import settings  # To reference the custom user model dynamically
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import random
import string

class CustomUserManager(BaseUserManager):
    """
    Custom manager for CustomUser.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model that uses email instead of username.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"  # Use email as the unique identifier
    REQUIRED_FIELDS = []      # No additional required fields

    def __str__(self):
        return self.email

class LabsActive(models.Model):
    """
    Table to store active labs with details.
    """
    lab_id = models.CharField(max_length=255, primary_key=True)  # Primary key for the table
    lab_name = models.CharField(max_length=255)  # Name of the lab
    start_time = models.DateTimeField(auto_now_add=True)  # When the lab started
    max_time = models.DurationField()  # Maximum time allowed for the lab
    allow_collab = models.BooleanField(default=False)  # Whether collaboration is allowed
    started_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference the custom user model
        on_delete=models.CASCADE,  # Delete labs if the user is deleted
        related_name="labs",       # Related name for reverse lookup
    )
    verification_token = models.CharField(max_length=12, unique=False, default='')  # Unique verification token

    def save(self, *args, **kwargs):
        if not self.verification_token:
            self.verification_token = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.lab_name} (ID: {self.lab_id}) started by {self.started_by.email}"

    
class Collaboration(models.Model):
    """
    Table to store collaborations for active labs.
    """
    lab = models.ForeignKey(
        LabsActive,
        to_field='lab_id',  # Explicitly reference the 'lab_id' column
        on_delete=models.CASCADE,
        related_name="collaborations",
    )

    collab_email = models.EmailField()  # Email of the collaborator
    permission = models.CharField(max_length=50, choices=[
        ('read', 'Read'),
        ('write', 'Write'),
        ('admin', 'Admin')
    ])  # Permission level
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f"Collaboration: {self.collab_email} on Lab ID {self.lab.lab_id} with {self.permission} permission"
