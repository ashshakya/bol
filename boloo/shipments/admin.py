from django.contrib import admin

from boloo.shipments.models import Order, Shipment, Transport


@admin.register(Shipment)
class ShipmentAdmin(admin.ModelAdmin):
    list_display = ('shipmentId', 'shipmentDate')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderItemId', 'orderId')


@admin.register(Transport)
class Transport(admin.ModelAdmin):
    list_display = ('transportId', 'transporterCode')
