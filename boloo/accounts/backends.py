import binascii

import json
import jwt
from django.conf import settings
from rest_framework import authentication, exceptions

from boloo.accounts.models import Seller


class JWTAuthentication(authentication.BaseAuthentication):
    """
        DRF authentication backend
    """
    authentication_header_prefix = 'Bearer'

    def authenticate(self, request):
        """
        The `authenticate` method is called on every request regardless of
        whether the endpoint requires authentication.

        `authenticate` has two possible return values:

        1) `None` - We return `None` if we do not wish to authenticate. Usually
                    this means we know authentication will fail. An example of
                    this is when the request does not include a token in the
                    headers.

        2) `(user, token)` - We return a user/token combination when
                             authentication is successful.

                            If neither case is met, that means there's an error
                            and we do not return anything.
                            We simple raise the `AuthenticationFailed`
                            exception and let Django REST Framework
                            handle the rest.
        """
        request.user = None

        # `auth_header` should be an array with two elements: 1) the name of
        # the authentication header (in this case, 'Token') and 2) the JWT
        # that we should authenticate against.
        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        if len(auth_header) > 2:
            # Invalid token header. No credentials provided. Do not attempt to
            # authenticate.
            return None

        # The JWT library we're using can't handle the `byte` type, which is
        # commonly used by standard libraries in Python 3. To get around this,
        # we simply have to decode `prefix` and `token`. This does not make for
        # clean code, but it is a good decision because we would get an error
        # if we didn't decode these values.
        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            # The auth header prefix is not what we expected. Do not attempt to
            # authenticate.
            return None

        # By now, we are sure there is a *chance* that authentication will
        # succeed. We delegate the actual credentials authentication to the
        # method below.
        return self._authenticate_credentials(request, token)

    def _authenticate_credentials(self, request, token):
        """
        Try to authenticate the given credentials. If authentication is
        successful, return the user and token. If not, throw an error.
        """
        try:
            user, secret_key = self._get_user_token_secret_key(token)
            # We only decode the token here, because the payload has already
            # been evaluated to get the user instance out from the database.
            # This will raise an exception if the token has been tampered with.
            jwt.decode(token, '{}{}'.format(secret_key, settings.SECRET_KEY))
        except jwt.exceptions.ExpiredSignatureError:
            msg = 'Authentication token has expired. Please login again to continue.'
            raise exceptions.AuthenticationFailed(msg)
        except Exception as e:
            msg = 'Invalid authentication. Could not decode token. %s', e
            raise exceptions.AuthenticationFailed(msg)

        if not user.is_active:
            msg = 'This user account is inactive.'
            raise exceptions.AuthenticationFailed(msg)

        return(user, token)

    def _get_user_token_secret_key(self, token):
        if isinstance(token, str):
            token = token.encode('utf-8')

        if not issubclass(type(token), bytes):
            raise jwt.exceptions.DecodeError('Invalid token type. Token must be a {0}'.format(
                bytes))

        try:
            payload_segment = jwt.utils.base64url_decode(
                token.rsplit(b'.', 1)[0].split(b'.', 1)[1]
            )
        except (TypeError, binascii.Error):
            raise jwt.exceptions.DecodeError('Invalid payload padding')
        except ValueError:
            raise jwt.exceptions.DecodeError('Not enough segments')

        payload_segment = json.loads(payload_segment.decode('utf-8'))

        try:
            user = Seller.objects.get(seller_code=payload_segment['id'])
        except Seller.DoesNotExist:
            msg = 'No user matching this token was found.'
            raise exceptions.AuthenticationFailed(msg)

        secret_key = str(user.client_id) + user.client_secret_key

        return user, secret_key
