from django.urls import path

from boloo.shipments.views import (
    SyncShipmentView, GetShipmentsView
)

urlpatterns = [
    path(
        'sync_shipment/', SyncShipmentView.as_view(), name='sync_shipment',
    ),
    path(
        'shipments/', GetShipmentsView.as_view(), name='shipment',
    ),
]
