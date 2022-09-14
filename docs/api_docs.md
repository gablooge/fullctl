# Regenerate api docs

src needs to be mounted as a volume to `main` for this to work

```
export SVC=devicectl
Ctl/dev/run.sh generateschema --file main/django_$SVC/static/docs/openapi.yaml
```
