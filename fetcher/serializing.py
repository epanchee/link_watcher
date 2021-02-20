import json
from abc import abstractmethod, ABCMeta


class Serializer(metaclass=ABCMeta):

    @staticmethod
    @abstractmethod
    def serialize(data):
        pass


class JsonSerializer(Serializer):

    @staticmethod
    def serialize(data):
        return json.dumps(data, ensure_ascii=False)
