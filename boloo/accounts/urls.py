from django.urls import path, re_path

# from .account_views import (RegisterationView, LoginView)
from boloo.accounts.views import (
    CreateCredentialsView,
    RegisterView,
    TokenView,
)


token = TokenView.as_view({
    'post': 'create',
})

credentials = CreateCredentialsView.as_view({
    'get': 'retrieve',
    'post': 'create',
    'delete': 'delete',
})


urlpatterns = [
    path('register', RegisterView.as_view(), name='register'),
    path('token', token, name='token'),
    # path(
    #     'credentials/', credentials, name='credentials'
    # ),
    re_path(
        r'credentials/(?P<seller_code>.+)',
        credentials,
        name='credentials-detail'
    ),
]
