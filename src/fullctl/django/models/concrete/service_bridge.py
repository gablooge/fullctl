from django.db import models
from django.utils.translation import gettext_lazy as _

from fullctl.django.models.abstract import HandleRefModel

__all__ = [
    "ServiceBridgeReference",
]

class ServiceBridgeReference(HandleRefModel):

    """
    Maps a service bridge class to a fullctl handle-ref model for either
    push or pull operations in a configurable fashion.
    """

    name = models.CharField(max_length=255, unique=True)
    reference = models.CharField(max_length=255, help_text=_("should be {module_path}.{class_name} of the service bridge class"))
    target = models.CharField(max_length=255, help_text=_("should be {app_label}.{mode_name} of the target model"))
    description = models.CharField(max_length=255, null=True, blank=True)
    operation = models.CharField(max_length=8, choices=(("pull", _("Pull")), ("push",_("Push"))), default="pull")

    class HandelRef:
        tag = "service_bridge_reference"

    class Meta:
        db_table = "fullctl_service_bridge_reference"
        verbose_name = _("Service Bridge Reference")
        verbose_name_plural = _("Service Bridge References")

    def __str__(self):
        return f"ServiceBridgeReference({self.name})[{self.reference} -> {self.target}]"
