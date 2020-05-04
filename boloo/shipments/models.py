
from django.db import models


class Fulfilment:
    FBR = 'FBR'
    FBB = 'FBB'


class Shipment(models.Model):

    shipmentId = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    shipmentDate = models.DateTimeField(null=True, blank=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class Order(models.Model):

    FULFILMENT_CHOICES = (
        (None, 'Choose a preferred language.'),
        (Fulfilment.FBR, ' Fulfilled by the retailer'),
        (Fulfilment.FBB, 'Fulfilled by bol.com'),
    )

    orderItemId = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    orderId = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    orderDate = models.DateTimeField(auto_now=True)
    latestDeliveryDate = models.DateTimeField(auto_now=True)
    ean = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    title = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    quantity = models.IntegerField(blank=True, null=True)
    offerPrice = models.FloatField(blank=True, null=True)
    offerCondition = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    fulfilmentMethod = models.CharField(
        choices=FULFILMENT_CHOICES, max_length=10,
        default=None, blank=True, null=True
    )

    shipment = models.ForeignKey(Shipment, on_delete=models.PROTECT)


class Transport(models.Model):

    shipment = models.OneToOneField(Shipment, on_delete=models.PROTECT)

    transportId = models.IntegerField(
        null=True, blank=True
    )
    transporterCode = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
    trackAndTrace = models.CharField(
        max_length=50, null=True, blank=True, unique=True
    )
