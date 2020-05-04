
from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response

from boloo.accounts.tasks import (
    fetch_shipment_from_boloo,
    fetch_shipment_details_from_boloo
)
from boloo.shipments.serializers import SyncShipmentSerializer
from boloo.shipments.models import Shipment


class SyncShipmentView(APIView):
    """ API to sync shipment data from bol.com
    """
    permission_classes = (permissions.AllowAny,)

    def get(self, request, shipment_id=None):
        if shipment_id is None:
            fetch_shipment_from_boloo.apply_async(paginator=0)
            return Response({
                'message': 'Fetching data...'
            })
        else:
            shipment = Shipment.objects.all()
            s = SyncShipmentSerializer(shipment, many=True)
            return Response(s.data)


class GetShipmentsView(APIView):
    """ API to get the shipment list
    """

    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        shipments = Shipment.objects.all()
        shipment = SyncShipmentSerializer(shipments, many=True)
        return Response(shipment.data)
