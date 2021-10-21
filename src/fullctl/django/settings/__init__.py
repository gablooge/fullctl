import os
import sys

import confu.util


# TODO : add dict access and logging
class SettingsManager(confu.util.SettingsManager):
    def print_debug(self, *args, **kwargs):
        if DEBUG:
            print(*args, **kwargs)


def print_debug(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)


def get_locale_name(code):
    """Gets the readble name for a locale code."""
    language_map = dict(django.conf.global_settings.LANGUAGES)

    # check for exact match
    if code in language_map:
        return language_map[code]

    # try for the language, fall back to just using the code
    language = code.split("-")[0]
    return language_map.get(language, code)


def try_include(filename):
    """Tries to include another file from the settings directory."""
    print_debug(f"including {filename} {RELEASE_ENV}")
    try:
        with open(filename) as f:
            exec(compile(f.read(), filename, "exec"), globals())

        print_debug(f"loaded additional settings file '{filename}'")

    except FileNotFoundError:
        print_debug(f"additional settings file '{filename}' was not found, skipping")


def read_file(name):
    with open(name) as fh:
        return fh.read()


def set_release_env_v1(settings_manager):
    """
    Sets release env for django service settings version 1.

    Version is an arbitrary number to define the defaults to allow for ease of service migration.
    """
    # set RELEASE_ENV, usually one of dev, beta, prod, run_tests
    settings_manager.set_option("RELEASE_ENV", "dev")
    release_env = settings_manager.scope["RELEASE_ENV"]

    # set DEBUG first, print_debug() depends on it
    if release_env == "dev":
        settings_manager.set_bool("DEBUG", True)
    else:
        settings_manager.set_bool("DEBUG", False)

    if release_env == "prod":
        # we only expose admin on non-production environments
        settings_manager.set_bool("EXPOSE_ADMIN", False)
    else:
        settings_manager.set_bool("EXPOSE_ADMIN", True)


def set_default_v1(settings_manager):
    """
    Sets default django service settings version 1.

    Version is an arbitrary number to define the defaults to allow for ease of service migration.
    """
    service_tag = settings_manager.scope["SERVICE_TAG"]

    # Contact email, from address, support email
    settings_manager.set_from_env("SERVER_EMAIL")

    # django secret key
    settings_manager.set_from_env("SECRET_KEY")

    # database

    settings_manager.set_option("DATABASE_ENGINE", "postgresql_psycopg2")
    settings_manager.set_option("DATABASE_HOST", "127.0.0.1")
    settings_manager.set_option("DATABASE_PORT", "")
    settings_manager.set_option("DATABASE_NAME", service_tag)
    settings_manager.set_option("DATABASE_USER", service_tag)
    settings_manager.set_option("DATABASE_PASSWORD", "")

    # email

    # default email goes to console
    settings_manager.set_option(
        "EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend"
    )
    # TODO EMAIL_SUBJECT_PREFIX = "[{}] ".format(RELEASE_ENV)

    settings_manager.set_from_env("EMAIL_HOST")
    settings_manager.set_from_env("EMAIL_PORT")
    settings_manager.set_from_env("EMAIL_HOST_USER")
    settings_manager.set_from_env("EMAIL_HOST_PASSWORD")
    settings_manager.set_bool("EMAIL_USE_TLS", True)

    # Application definition

    INSTALLED_APPS = [
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
    settings_manager.set_default("INSTALLED_APPS", INSTALLED_APPS)

    MIDDLEWARE = [
        "django.middleware.security.SecurityMiddleware",
        "whitenoise.middleware.WhiteNoiseMiddleware",
        "django.contrib.sessions.middleware.SessionMiddleware",
        "django.middleware.common.CommonMiddleware",
        "django.middleware.csrf.CsrfViewMiddleware",
        "django.contrib.auth.middleware.AuthenticationMiddleware",
        "django.contrib.messages.middleware.MessageMiddleware",
        "django.middleware.clickjacking.XFrameOptionsMiddleware",
        "fullctl.django.middleware.CurrentRequestContext",
    ]
    settings_manager.set_default("MIDDLEWARE", MIDDLEWARE)

    settings_manager.set_default("ROOT_URLCONF", f"{service_tag}.urls")
    settings_manager.set_default("WSGI_APPLICATION", f"{service_tag}.wsgi.application")
