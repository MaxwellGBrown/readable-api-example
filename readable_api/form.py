"""Form builder for API resources with POST operations."""
from webob.multidict import MultiDict
import wtforms

from readable_api.resources.base import LeafResource


def build_form(resource):
    """Construct a wtforms.form object from a JSON Schema."""
    schema = resource.schema

    properties = schema.get("properties", {})
    fields = dict()

    if schema["type"] != "object":
        properties["value"] = {"type": "string"}

    for name, sub_schema in properties.items():
        if sub_schema.get("generated", False):
            continue  # Don't create fields for generated values
        elif sub_schema.get("type") == "string":
            fields[name] = wtforms.fields.StringField(name)

    form_cls = type("Form", (wtforms.form.Form,), fields)

    # TODO This is a really shitty way to check if a resource is a leaf
    #      resource or a branch resource.
    if isinstance(resource, LeafResource):
        data = MultiDict(**resource.data)
        return form_cls(**data)

    return form_cls()
