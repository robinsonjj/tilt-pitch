from ..models import TiltStatus
from ..abstractions import CloudProviderBase
from ..configuration import PitchConfig
from ..rate_limiter import DeviceRateLimiter
from interface import implements
import requests
import json
import datetime


class BrewfatherTiltStreamCloudProvider(implements(CloudProviderBase)):

    def __init__(self, config: PitchConfig):
        self.url = config.brewfather_tilt_stream_url
        self.str_name = "Brewfather ({})".format(self.url)
        self.rate_limiter = DeviceRateLimiter(rate=1, period=(60 * 15))  # 15 minutes

    def __str__(self):
        return self.str_name

    def start(self):
        pass

    def update(self, tilt_status: TiltStatus):
        self.rate_limiter.approve(tilt_status.color)
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        payload = self._get_payload(tilt_status)
        result = requests.post(self.url, headers=headers, data=json.dumps(payload))
        result.raise_for_status()

    def enabled(self):
        return True if self.url else False

    def _get_timepoint(self, tilt_status: TiltStatus):
        diff = (tilt_status.timestamp - datetime.datetime(1899, 12, 30))
        return str(diff.days + diff.seconds/(3600*24))

    def _get_payload(self, tilt_status: TiltStatus):
        return {
            'Timepoint': self._get_timepoint(tilt_status),
            'SG': str(tilt_status.gravity),
            'Temp': str(tilt_status.temp_fahrenheit),
            'Color': tilt_status.color.upper(),
            'Beer': tilt_status.name
        }
