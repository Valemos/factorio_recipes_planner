from abc import abstractmethod
from typing import Type

from serialization.i_json_serializable import IJsonSerializable
from serialization.metaclasses import SingleTypeScheme


class AContainerJsonSerializable(IJsonSerializable, metaclass=SingleTypeScheme):
    __element_type__: Type[IJsonSerializable]

    @abstractmethod
    def __iter__(self):
        pass

    @abstractmethod
    def append(self, element):
        pass

    def to_json(self):
        return [elem.to_json() for elem in self]

    @classmethod
    def from_json(cls, json_object: list):
        result = cls()
        if IJsonSerializable.is_basic_type(cls.__element_type__):
            for value in json_object:
                result.append(value)
        else:
            for value in json_object:
                result.append(cls.__element_type__.from_json(value))
        return result
