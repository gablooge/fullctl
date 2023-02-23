"""
Abstract classes to facilitate the fetching, caching and retrieving of meta data
sourced from third party sources.
"""
import json
import time
import datetime
from datetime import timedelta, datetime

import confu.schema
import requests
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from fullctl.django.models.abstract import HandleRefModel

__all__ = [
    "Request",
    "Response",
    "Data",
]


class DataMixin:
    def clean_data(self):
        """
        If the model has a DataSchema confu schema
        defined, the schema will be used to validate the data
        in self.data
        """

        if not hasattr(self, "DataSchema"):
            return

        for name in dir(self.DataSchema):
            if name.startswith("_"):
                continue

            data = getattr(self, name)
            schema = getattr(self.DataSchema, name)

            try:
                confu.schema.validate(schema(), data, raise_errors=True)
            except confu.schema.ValidationError as exc:
                raise ValidationError(f"Invalid meta-data in {name}: {exc}")


class Data(HandleRefModel):

    """
    Normalized object meta data
    """

    source_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, default="info")
    data = models.JSONField()
    date = models.DateTimeField(help_text="Data validity start date")

    class Meta:
        abstract = True

    class HandleRef:
        tag = "meta_data"

    class Config:
        # historic period in seconds
        period = 12 * 3600
        type = "info"

    @classmethod
    def cleanup(cls, target=None, age=None):
        return

    @classmethod
    def config(cls, config_name, default=None):
        value = getattr(cls.Config, config_name, default)

        if value is None:
            raise ValueError(f"`{cls}.Config.{config_name}` property not specified")

        return value

    def update(self, data):
        self.data = data


class Request(HandleRefModel):

    """
    Handles logic for requesting and rate-throttling third party meta data
    """

    source = models.CharField(max_length=255)
    type = models.CharField(max_length=255, null=True, blank=True)
    url = models.URLField()
    http_status = models.PositiveIntegerField()
    payload = models.JSONField(null=True)
    count = models.PositiveIntegerField(default=1)

    processing_error = models.CharField(
        max_length=255,
        help_text="will hold error information if the request came back as a success but reading its data resulted in an error on our end.",
        null=True,
        blank=True,
    )

    class Config:
        cache_expiry = 86400
        source_name = None

    class HandleRef:
        tag = "meta_request"

    class Meta:
        abstract = True

    @classmethod
    def prepare_request(cls, targets):
        """
        will make sure targets are always converted
        into a list object

        override this method for more complex preparation
        of request targets

        Arguments:

        - targets (`list|mixed`)

        Returns:

        - targets (`list`)
        """

        if not isinstance(targets, list):
            return [targets]
        return targets

    @classmethod
    def request(cls, targets):
        """
        Requests data for one or more targets

        This will honor both request and response cache layers
        """

        targets = cls.prepare_request(targets)
        results = {}

        for target in targets:
            results[f"{target}"] = cls.request_target(target)

        return results

    @classmethod
    def request_target(cls, target, ignore_cache=False):
        """
        Requests data for the specified target

        This will honor both request and response cache layers and will
        return the `Request` instance for it if exists and is valid.

        Arguments:

        - target: the target of the request, will be processed through `target_to_url`
          class method to convert into a requestable url.

        Keyword arguments:

        - ignore_cache (`bool`): if True both cache layers will be ignored


        Returns:

        - request (`Request`)
        """

        request = cls.get_cache(target)

        if request:
            return cls.process(target, request.url, request.http_status, request.response.data, cached=True)

        return cls.send(target)

    @classmethod
    def target_to_url(cls, target):
        """
        override this to handle converting a target to a requestable url
        """

        raise NotImplementedError()

    @classmethod
    def target_to_type(cls, target):
        """
        override this to handle converting a target to a requestable url
        """
        return None


    @classmethod
    def send(cls, target):
        """
        Send request to third party api to retrieve data for target.

        In some cases it may make sense to override this in an extended class
        to implemnt more complex fetching logic.

        In this impementation a GET request is sent off using the `requests`
        module and expecting a json response.
        """

        url = cls.target_to_url(target)

        print("seding request to", url, " - target - ", target)
        _resp = cls.send_request(url)

        return cls.process(target, url, _resp.status_code, lambda: _resp.json())

    @classmethod
    def send_request(cls, url):
        return requests.get(url)

    @classmethod
    def process(cls, target, url, http_status, getdata, payload=None, cached=False):
        """
        processes a response and return the `Request` object created for it
        """

        source = cls.config("source_name")
        target_field = cls.config("target_field")
        response_cls = cls._meta.get_field("response").related_model

        params = {target_field: target, "url": url, "source": source, "type": cls.target_to_type(target)}

        if payload:
            params.update(payload=json.dumps(payload))

        try:
            req = cls.objects.get(**params)
            created = False
        except cls.DoesNotExist:
            req = cls(**params)
            created = True

        if not created:
            req.count += 1

        data = None

        req.http_status = http_status

        try:
            if callable(getdata):
                data = getdata()
            else:
                data = getdata
        except Exception as exc:
            req.processing_error = f"{exc}"

        if not cached:
            req.save()

        if data is not None:
            try:
                req.response
                create_response = False
            except Exception:
                create_response = True

            if not create_response:
                req.response.data = data
                req.response.save()
            else:
                response_cls.objects.create(
                    source=source,
                    data=data,
                    request=req,
                )

            req.response.write_meta_data(req)

            return req

        return req

    @classmethod
    def config(cls, config_name, default=None):
        value = getattr(cls.Config, config_name, default)

        if value is None:
            raise ValueError(f"`{cls}.Config.{config_name}` property not specified")

        return value

    @classmethod
    def get_cache(cls, target):
        qset = cls.get_cache_queryset(target)
        qset = qset.filter(updated__gte=cls.valid_cache_datetime())

        if qset.exists():
            return qset.first()

        return None

    @classmethod
    def get_cache_queryset(cls, target):
        target_field = cls.config("target_field")
        typ = cls.target_to_type(target)
        filters = {target_field: target, "source": cls.config("source_name")}

        if typ:
            filters.update(type=typ)
        else:
            filters.update(type__isnull=True)

        return cls.objects.filter(**filters)

    @classmethod
    def cache_expiry(cls):
        return cls.config("cache_expiry")

    @classmethod
    def valid_cache_datetime(cls):
        expiry = cls.cache_expiry()
        return timezone.now() - timedelta(seconds=expiry)

    def process_response(self, response, target, date):
        yield date, target, response.data

    def prepare_data(self, data):
        return data


class Response(HandleRefModel):

    """
    Maintains a cache for third party data responses
    """

    source = models.CharField(max_length=255)
    data = models.JSONField(null=True)

    class Config:
        meta_data_cls = None

    class Meta:
        abstract = True

    class HandleRef:
        tag = "meta_response"

    @classmethod
    def config(cls, config_name, default=None):
        value = getattr(cls.Config, config_name, default)

        if value is None:
            raise ValueError(f"`{cls}.Config.{config_name}` property not specified")

        return value

    @property
    def meta_data_cls(self):
        return self.request.config("meta_data_cls", self.config("meta_data_cls"))

    def write_meta_data(self, req):
        meta_data_cls = self.meta_data_cls
        target_field = self.config("target_field", req.config("target_field"))
        source_name = req.config("source_name")
        target = getattr(req, target_field)

        for date, _target, data in req.process_response(self, target, timezone.now()):
            self._write_meta_data(req, date, req.prepare_data(data), _target, target_field, source_name)

        meta_data_cls.cleanup(target=target)


    def _write_meta_data(self, request, date, data, target, target_field, source_name):

        meta_data_cls = self.meta_data_cls
        meta_data_type = meta_data_cls.config("type")
        period = meta_data_cls.config("period")
        start = date - timedelta(seconds=period)
        end = date + timedelta(seconds=period)

        filters = {target_field: target, "source_name": source_name}
        meta_data = meta_data_cls.objects.filter(date__gte=start, date__lte=end).filter(**filters).first()


        if not meta_data:
            meta_data = meta_data_cls(data={}, source_name=source_name, date=date)
            setattr(meta_data, target_field, target)

        meta_data.data = data
        meta_data.type = meta_data_type

        meta_data.save()

