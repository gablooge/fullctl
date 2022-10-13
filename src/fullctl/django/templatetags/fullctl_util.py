from django import template

from fullctl.django.context import current_request

register = template.Library()


@register.filter
def can_read(request, namespace):
    namespace = namespace.format(org=request.org)
    return request.perms.check(namespace, "r")


@register.filter
def can_create(request, namespace):
    namespace = namespace.format(org=request.org)
    return request.perms.check(namespace, "c")


@register.filter
def can_update(request, namespace):
    namespace = namespace.format(org=request.org)
    return request.perms.check(namespace, "u")


@register.filter
def can_delete(request, namespace):
    namespace = namespace.format(org=request.org)
    return request.perms.check(namespace, "d")


@register.filter
def themed_path(path):

    with current_request() as request:
        if not request:
            return path

        try:
            theme = request.user.settings.theme
        except AttributeError:
            return path

        if theme:
            parts = path.split("/")
            if len(parts) == 1:
                parts.prepend(theme)
            else:
                parts.insert(1, theme)
            path = "/".join(parts)
        return path


