# Regenerate api docs

## Settings


### Include service-bridge endpoints

By default `service-bridge` endpoints will not be included in the documentation that is generated.

This behaviour is controlled by the `API_DOCS_GENERATE_SERVICE_BRIDGE` setting. Set to `True` or `1` to include service-bridge
endpoints in the api documenation.

## Generate

`src` needs to be mounted as a volume to `main` for this to work

```
export SVC=devicectl
Ctl/dev/run.sh generateschema --generator_class fullctl.django.rest.api_schema.SchemaGenerator --file main/django_$SVC/static/docs/openapi.yaml
```
