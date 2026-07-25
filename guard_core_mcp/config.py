import difflib
import importlib
import importlib.metadata
import typing
import warnings
from typing import Any

from pydantic import BaseModel, ValidationError
from pydantic.fields import FieldInfo, PydanticUndefined

PACKAGE_MODELS: dict[str, tuple[str, str]] = {
    "guard-core": ("guard_core", "SecurityConfig"),
    "fastapi-guard": ("guard", "SecurityConfig"),
    "guard-agent": ("guard_agent", "AgentConfig"),
}


def resolve_model(package: str) -> tuple[type[BaseModel], str | None]:
    if package not in PACKAGE_MODELS:
        raise ValueError(
            f"unknown package {package!r}; expected one of {', '.join(PACKAGE_MODELS)}"
        )
    module_name, attribute = PACKAGE_MODELS[package]
    module = importlib.import_module(module_name)
    model: type[BaseModel] = getattr(module, attribute)
    try:
        version: str | None = importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        version = None
    return model, version


def _format_annotation(annotation: Any) -> str:
    origin = typing.get_origin(annotation)
    args = typing.get_args(annotation)

    if origin is None:
        name = getattr(annotation, "__name__", None)
        if name is not None:
            return str(name)
        return str(annotation).replace("typing.", "")

    origin_name = getattr(origin, "__name__", None) or str(origin).replace(
        "typing.", ""
    )
    if not args:
        return origin_name

    formatted_args = ", ".join(_format_annotation(argument) for argument in args)
    return f"{origin_name}[{formatted_args}]"


def _serialize_default(default: Any) -> str | None:
    if default is PydanticUndefined or default is None:
        return None
    return repr(default)


def describe_field(name: str, info: FieldInfo) -> dict[str, Any]:
    return {
        "name": name,
        "type": _format_annotation(info.annotation),
        "default": _serialize_default(info.default),
        "required": info.is_required(),
        "description": info.description,
    }


def _deprecation_entry(message: str, known_fields: set[str]) -> dict[str, str | None]:
    first_token = message.split(maxsplit=1)[0]
    return {
        "field": first_token if first_token in known_fields else None,
        "message": message,
    }


def parse_validation_error(exception: ValidationError) -> list[dict[str, Any]]:
    return [
        {
            "field": ".".join(str(part) for part in error["loc"]),
            "message": error["msg"],
            "input": repr(error.get("input")),
        }
        for error in exception.errors()
    ]


def validate_config(
    config: dict[str, Any], package: str = "fastapi-guard"
) -> dict[str, Any]:
    model, version = resolve_model(package)
    known_fields = set(model.model_fields)

    unknown_fields = [
        {
            "name": key,
            "did_you_mean": difflib.get_close_matches(
                key, known_fields, n=3, cutoff=0.75
            ),
        }
        for key in config
        if key not in known_fields
    ]

    errors: list[dict[str, Any]] = []
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        try:
            model(**config)
        except ValidationError as exception:
            errors = parse_validation_error(exception)

    deprecated = [
        _deprecation_entry(str(warning.message), known_fields)
        for warning in caught
        if issubclass(warning.category, DeprecationWarning)
    ]

    return {
        "valid": not errors and not unknown_fields,
        "package": package,
        "version": version,
        "model": model.__name__,
        "errors": errors,
        "unknown_fields": unknown_fields,
        "deprecated": deprecated,
    }


def config_fields(query: str, package: str = "fastapi-guard") -> dict[str, Any]:
    model, version = resolve_model(package)
    fields = model.model_fields

    exact = describe_field(query, fields[query]) if query in fields else None

    tokens = query.lower().split()
    matches = [
        describe_field(name, info)
        for name, info in fields.items()
        if name != query
        and all(token in f"{name} {info.description or ''}".lower() for token in tokens)
    ]

    if not matches and exact is None:
        matches = [
            describe_field(name, fields[name])
            for name in difflib.get_close_matches(query, list(fields), n=5)
        ]

    return {
        "package": package,
        "version": version,
        "query": query,
        "exact": exact,
        "matches": matches,
    }
