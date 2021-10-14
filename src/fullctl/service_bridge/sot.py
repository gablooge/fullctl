"""
Retrieve data from the source of truth

Currently this covers internet exchange member information which either
exists in pdbctl (peeringdb data) or ixctl, but could be extended on
further down the line
"""

from fullctl.service_bridge.client import ServiceBridgeError

import fullctl.service_bridge.pdbctl as pdbctl
import fullctl.service_bridge.ixctl as ixctl

SOURCE_MAP = {
    "member": {
        "pdbctl": pdbctl.NetworkIXLan,
        "ixctl": ixctl.InternetExchangeMember
    },
    "ix": {
        "pdbctl": pdbctl.InternetExchange,
        "ixctl": ixctl.InternetExchange
    }
}

class SourceOfTruth:
    sources = []
    key = ("id",)

    def make_key(self, obj):
        return (getattr(obj, k) for k in self.key)

    def object(self, *args, **kwargs):
        for source, params in self.sources:
            kwargs.update(params)
            kwargs["raise_on_notfound"] = False
            try:
                return source().object(*args, **kwargs)
            except ServiceBridgeError as exc:
                if exc.status == 404:
                    continue
                raise
        if kwargs.get("raise_on_notfound"):
            raise KeyError("Object does not exist")

    def objects(self, **kwargs):

        _result = []
        _index = {}

        for source, params in self.sources:
            kwargs.update(params)
            try:
                for obj in source().objects(**kwargs):
                    key = self.make_key(obj)
                    if key not in _index:
                        _result.append(obj)
                        _index[key] = obj

            except ServiceBridgeError as exc:
                if exc.status == 404:
                    continue
                raise

    def first(self, **kwargs):
        for o in self.objects(**kwargs):
            return o


class InternetExchangeMember(SourceOfTruth):

    key = ("asn", "ipaddr4", "ipaddr6")

    sources = [
        (ixctl.InternetExchangeMember, {"sot":True}),
        (pdbctl.NetworkIXLan, {}),
    ]


