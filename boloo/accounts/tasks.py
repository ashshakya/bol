"""
Celery task to get the shipments data asynchronously.
"""
from collections import Iterable

import requests

from celery import group, shared_task
from celery.utils.log import get_task_logger
from django.conf import settings

from boloo.accounts.tokens import get_access_token
from boloo.shipments.serializers import SyncShipmentSerializer
from boloo.shipments.models import Shipment

logger = get_task_logger(__name__)


@shared_task(ignore_result=True)
def fetch_shipment_from_boloo(paginator=0):
    job = group(fetch_shipment.si(paginator=paginator))
    job.apply_async()
    logger.info(
        "Fetch Shipment from Boloo Task ID is: %s" %
        fetch_shipment_from_boloo.request.id
    )


def get_header():
    """
    Get Header details
    """
    headers = {
        'Content-Type': 'application/vnd.retailer.v3+json',
        'Accept': 'application/vnd.retailer.v3+json',
    }
    access_token = get_access_token()
    if access_token:
        headers.update(access_token)
    return headers


@shared_task(ignore_result=True)
def fetch_shipment(paginator=0):

    header = get_header()
    while True:
        paginator += 1
        response = requests.get(
            url=settings.BOLOO_URLS['SHIPMENT_LIST_URL'],
            headers=header,
            params={'page': paginator}
        )
        if response.status_code == 200:
            response = response.json()
            if response.get('shipments'):
                serializer = SyncShipmentSerializer(
                    data=response['shipments'], many=True
                )
                serializer.is_valid(raise_exception=True)
                serializer.save()
                continue
            else:  # Break if no data found
                break
        elif response.status_code == 429:  # reach limit
            logger.info('Limit Reached now waiting.')
            fetch_shipment_from_boloo.apply_async(
                countdown=60, paginator=paginator
            )
        elif response.status_code == 401:
            header = get_header()
        break
    logger.info(
        'Total pages scrapped: %s' % (paginator - 1)
    )


@shared_task(ignore_result=True)
def fetch_shipment_details_from_boloo(shipment=None):
    if shipment is None:
        shipment = Shipment.objects.filter(
            transport__trackAndTrace__isnull=True
        ).values('shipmentId')
        shipment = list(shipment)
    job = group(fetch_shipment_datails.si(shipment))
    job.apply_async()
    logger.info(
        "Fetch Shipment details from Boloo Task ID is: %s" %
        fetch_shipment_from_boloo.request.id
    )


# @shared_task(ignore_result=True)
def fetch_shipment_datails(shipment_id_list):

    header = get_header()
    if not isinstance(shipment_id_list, Iterable):
        shipment_id_list = [shipment_id_list]
    while True:
        for shipment_id in shipment_id_list:
            s_id = shipment_id['shipmentId']
            response = requests.get(
                url=settings.BOLOO_URLS['SHIPMENT_LIST_URL'] + f'{s_id}',
                headers=header
            )
            if response.status_code == 401:
                header = get_header()
                continue  # continue loop and retry
            elif response.status_code == 200:
                response = response.json()
                if response.get('shipments'):
                    shipment = SyncShipmentSerializer(
                        data=response['shipments'], many=True
                    )
                    if shipment.is_valid():
                        shipment.save()
        # break loop when everything is fine
        break
