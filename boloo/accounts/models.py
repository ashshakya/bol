from datetime import datetime, timedelta
import jwt
import secrets
import uuid

from django.conf import settings
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.management.utils import get_random_secret_key


class Seller(AbstractBaseUser):
    """
    model for saving seller information
    """

    seller_name = models.CharField(
        max_length=128, blank=True, null=True, default=''
    )
    seller_code = models.CharField(
        max_length=64, unique=True, blank=True,
        null=True, editable=False, db_index=True
    )

    email = models.EmailField(
        max_length=256, unique=True,
        blank=True, null=True, db_column='email'
    )
    client_id = models.UUIDField(
        null=True, blank=True, default=uuid.uuid4, unique=True
    )
    client_secret_key = models.CharField(
        max_length=128, null=True, blank=True, unique=True
    )
    access_token = models.CharField(
        max_length=1000, null=True, blank=True, unique=True
    )

    USERNAME_FIELD = 'email'

    class Meta:
        verbose_name_plural = 'Sellers'

    def __str__(self):
        return f'{self.email}'

    def save(self, *args, **kwargs):
        is_new = False

        if self.id is None:
            is_new = True
        elif not self.seller_code:
            self.seller_code = self.create_seller_code()

        super().save(*args, **kwargs)

        if is_new and not self.seller_code:
            self.seller_code = self.create_seller_code()
            super().save()

    def generate_client_secret_key(self):
        """
            Create a client secret key for the seller.
        """
        if not self.client_id:
            self.client_id = uuid.uuid4()
            self.save
        if not self.client_secret_key:
            client_secret_key = secrets.token_urlsafe(76) + self.seller_code
            self.client_secret_key = client_secret_key
            self.save()
        return self.client_secret_key

    def create_seller_code(self, prefix='SI'):
        """
            Create a seller code for the seller.
        """
        return f'{prefix}{str(self.pk).zfill(10 - len(prefix))}'

    def _get_access_token(self):
        """
            Generates the final secret key used to create the seller's token,
            combining the credentials stored in the database and django's
            secret key from the settings.
        """
        return str(self.client_id) + self.client_secret_key + settings.SECRET_KEY

    def _generate_jwt_token(self):
        """
            Generates a JSON Web Token that stores this seller's ID and has an
            expiry date set to 299 seconds into the future.
        """
        dt = datetime.now() + timedelta(seconds=settings.ACCESS_TOKEN_EXPIRES)

        token = jwt.encode({
            'id': self.seller_code,
            'exp': int(dt.timestamp())
        }, self._get_access_token(), algorithm='HS256')

        return token.decode('utf-8')

    def refresh_access_token(self):
        """
            Updates the access token.
        """
        self.access_token = self._generate_jwt_token()
        self.save()
        return self.access_token
