import time

from beacontools import BeaconScanner, IBeaconFilter, IBeaconAdvertisement, parse_packet
from .models import TiltStatus, WebhookPayload
from .abstractions import CloudProviderBase
from .providers import PrometheusCloudProvider

# statics
color_map = {
        "a495bb20-c5b1-4b44-b512-1370f02d74de": "green",
        "a495bb30-c5b1-4b44-b512-1370f02d74de": "black",
        "a495bb10-c5b1-4b44-b512-1370f02d74de": "red",
        "a495bb60-c5b1-4b44-b512-1370f02d74de": "blue",
        "a495bb50-c5b1-4b44-b512-1370f02d74de": "orange",
        "a495bb70-c5b1-4b44-b512-1370f02d74de": "pink",
        "a495bb40-c5b1-4b44-b512-1370f02d74de": "purple"
    }
#########

def beacon_callback(bt_addr, rssi, packet, additional_info):
    uuid = packet.uuid
    color = color_map.get(uuid)
    if color:
        # iBeacon packets have major/minor attributes with data
        # major = degrees in F (int)
        # minor = gravity (int) - needs to be converted to float (e.g. 1035 -> 1.035)
        tilt_status = TiltStatus(color, packet.major, get_decimal_gravity(packet.minor))
        tilt_metrics(tilt_status)
        tilt_hooks(tilt_status)

def tilt_metrics(tilt_status: TiltStatus):
    temp = PrometheusCloudProvider()
    temp.log(tilt_status)

def tilt_hooks(tilt_status: TiltStatus):
    print("-------------------------------------------")
    print("Broadcoast for device:   {}".format(tilt_status.color))
    print("Temperature:             {}f ({}c)".format(tilt_status.temp_f, tilt_status.temp_c))
    print("Gravity:                 {}".format(tilt_status.gravity))
    print("Json:                    {}".format(WebhookPayload(tilt_status).json()))

def get_decimal_gravity(gravity):
    # gravity will be an int like 1035
    # turn into decimal, like 1.035
    return gravity * .001