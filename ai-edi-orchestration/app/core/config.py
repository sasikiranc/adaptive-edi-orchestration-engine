import os
import json

def get_xsuaa_config():
    vcap_services = os.getenv("VCAP_SERVICES")
    if not vcap_services:
        raise Exception("VCAP_SERVICES not found")
    
    services = json.loads(vcap_services)
    xsuaa = services["xsuaa"][0]["credentials"]
    return xsuaa

DEFAULT_THRESHOLD = 0.75

MIN_HISTORY_THRESHOLD = 3