from typing import Any, Callable, Iterable, Optional, Union, Collection, Type

from django.db.models.base import Model

from django.db import IntegrityError
from django.db.models.fields import Field
from django.db.models.options import Options

def CASCADE(collector, field, sub_objs, using): ...
def SET_NULL(collector, field, sub_objs, using): ...
def SET_DEFAULT(collector, field, sub_objs, using): ...
def DO_NOTHING(collector, field, sub_objs, using): ...
def PROTECT(collector, field, sub_objs, using): ...
def SET(value: Any) -> Callable: ...
def get_candidate_relations_to_delete(opts: Options) -> Iterable[Field]: ...

class ProtectedError(IntegrityError): ...

class Collector:
    def __init__(self, using: str) -> None: ...
    def collect(
        self,
        objs: Collection[Optional[Model]],
        source: Optional[Type[Model]] = ...,
        nullable: bool = ...,
        collect_related: bool = ...,
        source_attr: Optional[str] = ...,
        reverse_dependency: bool = ...,
        keep_parents: bool = ...,
    ) -> None: ...
    def can_fast_delete(self, objs: Union[Model, Iterable[Model]], from_field: Optional[Field] = ...) -> bool: ...
