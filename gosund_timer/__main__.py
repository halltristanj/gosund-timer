import json
from time import sleep
import logging
import sys
import os
from botocore.vendored import requests
from typing import Dict, List, Union


logging.basicConfig(
    stream=sys.stdout,
    level=logging.INFO,
    format='%(asctime)s [ %(levelname)s ] %(name)s %(funcName)s::%(lineno)s %(message)s',
)
LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


UNIT_MAPPING: Dict[str, List[str]] = {
    'minutes': ['min', 'mins', 'minute', 'minutes'],
    'seconds': ['sec', 'secs', 'second', 'seconds'],
}


def get_unit(unit: str) -> str:
    for key, values in UNIT_MAPPING.items():
        if unit in values:
            return key
    return 'Not-Found'


def wait_and_sleep(duration: int) -> None:
    i = 0
    while i <= duration:
        sleep(1)
        if i % 10 == 0:
            LOGGER.info(f'We have slept: {i} seconds')

        i += 1


def lambda_handler(event, context) -> Dict[str, Union[str, int]]:
    p = event.get('what')
    duration = int(event.get('duration'))
    unit = get_unit(event.get('unit'))

    LOGGER.info(f"Duration: {duration} | Unit: {unit}")

    if unit == 'minutes':
        duration = duration * 60

    LOGGER.info(f"Warming a bottle for {duration} s")

    if not unit:
        return {"statusCode": 401}

    if p != os.getenv("BOTTLE_WARMER"):
        return {
            'statusCode': 400,
            'body': 'go away',
        }

    wait_and_sleep(duration)

    response = requests.post(f"https://maker.ifttt.com/trigger/turn_off_bottle_warmer/with/key/{os.getenv('IFTTT_KEY')}")

    return {
        'statusCode': response.status_code,
        'body': json.dumps(response.text)
    }
