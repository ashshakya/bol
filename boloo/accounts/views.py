from django.shortcuts import get_object_or_404
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import (
    ValidationError
)

from boloo.accounts.serializers import SellerSerializer, TokenSerializer
from boloo.accounts.models import Seller


class RegisterView(APIView):
    """
        API to register the seller by using basic detials.
        ::params: seller_name
        ::params: email
        ::params: password

        ::return: seller_name
        ::return: seller_code
        ::return: email
    """
    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = SellerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


class CreateCredentialsView(viewsets.ViewSet):
    """
        CRUD API for seller credentials.
    """
    permission_classes = (permissions.AllowAny,)
    serializer_class = SellerSerializer

    def create(self, request, seller_code):
        seller = get_object_or_404(Seller, seller_code=seller_code)
        seller.generate_client_secret_key()
        serializer = SellerSerializer(seller)
        return Response(serializer.data)

    def retrieve(self, request, seller_code=None):
        seller = get_object_or_404(Seller, seller_code=seller_code)
        serializer = SellerSerializer(seller)
        return Response(serializer.data)

    def delete(self, request, seller_code=None):
        seller = get_object_or_404(Seller, seller_code=seller_code)
        seller.client_id = None
        seller.client_secret_key = None
        seller.save()
        serializer = SellerSerializer(seller)
        return Response(serializer.data)


class TokenView(viewsets.ViewSet):
    """
        API for creating access token used by the seller
        to fetch data.
    """

    permission_classes = (permissions.AllowAny,)

    def create(self, request):

        grant_type = request.query_params.get('grant_type')
        if grant_type != 'client_credentials':
            raise ValidationError('Please provide valid grant_type.')
        client_id = request.data.get('client_id')
        client_secret_key = request.data.get('client_secret_key')
        if not (client_id and client_secret_key):
            raise ValidationError('Please provide credentials.')

        serializer = TokenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response(serializer.data)

    def delete(self, request):
        grant_type = request.query_params.get('grant_type')
        if grant_type != 'client_credentials':
            raise ValidationError('Please provide valid grant_type.')
