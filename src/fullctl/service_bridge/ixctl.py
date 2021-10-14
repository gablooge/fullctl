try:
    from django.conf import settings
    DEFAULT_SERVICE_KEY = settings.SERVICE_KEY
except ImportError:
    DEFAULT_SERVICE_KEY = ""

from fullctl.service_bridge.client import Bridge, DataObject

CACHE = {}

class IxctlEntity(DataObject):
    source = "ixctl"
    description = "Ixctl Object"



class Ixctl(Bridge):

    """
    Service bridge for ixctl data retrieval
    """

    class Meta:
        service = "ixctl"
        ref_tag = "base"
        data_object_cls = IxctlEntity

    def __init__(self, key=None, org=None, **kwargs):

        if not key:
            key = DEFAULT_SERVICE_KEY


        kwargs.setdefault("cache_duration", 5)
        kwargs.setdefault("cache", CACHE)

        super().__init__(settings.IXCTL_HOST, key, org, **kwargs)
        self.url = f"{self.url}/service-bridge/data"


class InternetExchange(Ixctl):
    class Meta(Ixctl.Meta):
	    ref_tag = "ix"


class InternetExchangeMember(Ixctl):
    class Meta(Ixctl.Meta):
	    ref_tag = "member"
