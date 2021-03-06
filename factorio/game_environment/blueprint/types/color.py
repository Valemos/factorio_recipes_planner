from dataclasses import dataclass

from json_automatic.a_composite_json_serializable import ACompositeJsonSerializable


@dataclass
class Color(ACompositeJsonSerializable):
    r: float = None
    g: float = None
    b: float = None
    a: float = None
