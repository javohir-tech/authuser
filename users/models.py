import uuid
import random
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import identify_hasher
from rest_framework_simplejwt.tokens import RefreshToken
from shared.models import BaseModel


# hashing function
def is_hashed(password):
    try:
        identify_hasher(password)
        return True
    except Exception:
        return False


class User_Role(models.TextChoices):
    ORDENARY_USER = "ordanary_user", "Ordenary  User"
    ADMIN = "admin", "Admin"
    MANAGER = "manager", "Manager"


class AUTH_TYPE(models.TextChoices):
    VIA_EMAIL = "via_email", "Via Email"
    VIA_PHONE = "via_phone", "Via Phone"


class AUTH_STATUS(models.TextChoices):
    NEW = "new", "NEW"
    CODE_VERIFED = "code_verifed", "Code Verifed"
    DONE = "done", "Done"
    PHOTO = "photo", "Photo"


class User(AbstractUser, BaseModel):

    user_role = models.CharField(
        max_length=31, choices=User_Role.choices, default=User_Role.ORDENARY_USER
    )
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE.choices)
    auth_status = models.CharField(
        max_length=31, choices=AUTH_STATUS.choices, default=AUTH_STATUS.NEW
    )
    phone = models.CharField(max_length=13, blank=True, null=True, unique=True)
    email = models.EmailField(blank=True, null=True, unique=True)
    photo = models.ImageField(blank=True, null=True, upload_to="users_photo")

    def __str__(self):
        return self.username

    def create_user_confirmation(self, auth_type):
        code = "".join([str(random.randint(1, 10000) % 10) for _ in range(4)])
        UserConfirmation.objects.create(code=code, auth_type=auth_type, user=self)
        return code

    def check_username(self):
        if not self.username:
            temp_username = f"instagram-{uuid.uuid4.__str__().split("-")[-1]}"
            while User.objects.filter(username=temp_username):
                temp_username = f"{temp_username}{random.random(1, 9)}"
            self.username = temp_username

    def check_email(self):
        if self.email :
            normalize_email = self.email.lower()
            self.email = normalize_email

    def check_passwords(self ):
        if not self.password:
            temp_password = f"password-{uuid.uuid4.__str__().split("-")[-1]}"
            self.password = temp_password

    def check_password_hashed(self):
        if self.password and not is_hashed(self.password):
            self.set_password(self.password)

    def Token(self):
        refresh = RefreshToken.for_user(self)
        return {"access_token": refresh.access_token, "refresh": refresh}

    def clean(self):
        self.check_username()
        self.check_email()
        self.check_passwords()
        self.check_password_hashed()

    def save(self, *args, **kwargs):
        if not self.pk:
            self.clean()
        else:
            self.check_email()

        super(User, self).save(*args, **kwargs)


EXPIRE_EMAIL = 5
EXPIRE_PHONE = 2


class UserConfirmation(BaseModel):

    code = models.CharField(max_length=4)
    auth_type = models.CharField(max_length=31, choices=AUTH_TYPE.choices)
    user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="varify_codes"
    )
    expiration_time = models.DateTimeField(null=True)
    is_confirmation = models.BooleanField(default=False)

    def __str__(self):
        return str(self.user.__str__())

    def save(self, *args, **kwargs):
        if not self.pk:
            if self.auth_type == AUTH_TYPE.VIA_EMAIL:
                self.expiration_time = timezone.now() + timedelta(minutes=EXPIRE_EMAIL)
            if self.auth_type == AUTH_TYPE.VIA_PHONE:
                self.expiration_time = timezone.now() + timedelta(minutes=EXPIRE_PHONE)
            super(UserConfirmation, self).save(*args, **kwargs)


# Create your models here.
