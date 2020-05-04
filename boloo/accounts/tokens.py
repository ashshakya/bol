import requests

from django.conf import settings


CLIENT_ID = settings.BOLOO_CLIENT_ID
CLIENT_SECRET_KEY = settings.BOLOO_CLIENT_SECRET_KEY


def get_access_token():
    """
    Method used to get the fresh token from bol.com
    """

    header = {
        'Accept': 'application/json'
    }
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET_KEY
    }

    response = requests.post(
        url=settings.BOLOO_URLS['ACCESS_TOKEN_URL'],
        data=data,
        headers=header
    )

    if response.status_code != 200:
        return False

    return {
        'Authorization': '{token_type} {access_token}'.format(
            token_type=response.json().get('token_type'),
            access_token=response.json().get('access_token')
        )
    }
