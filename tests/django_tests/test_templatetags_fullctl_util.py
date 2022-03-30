from django.test import RequestFactory
from django_grainy.util import Permissions

import fullctl.django.templatetags.fullctl_util as fullctl_util


def test_can_read(db, dj_account_objects):
    factory = RequestFactory()
    request = factory.get("/test")
    request.org = dj_account_objects.org
    user = dj_account_objects.user
    user.grainy_permissions.add_permission_set({"org.1": "c"})
    request.perms = Permissions(user)

    assert fullctl_util.can_read(request, "org.1") is False

    user.grainy_permissions.add_permission_set({"org.1": "r"})
    request.perms = Permissions(user)

    assert fullctl_util.can_read(request, "org.1") is True
