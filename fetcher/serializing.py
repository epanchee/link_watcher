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


class PlainTextSerializer(Serializer):

    @staticmethod
    def __serialize(data):
        ret_val = ""

        if isinstance(data, list) or isinstance(data, tuple):
            ret_val += " ".join([PlainTextSerializer.__serialize(item) for item in data])
        elif isinstance(data, dict):
            ret_val += " | ".join(
                [f"{key}: {PlainTextSerializer.__serialize(value)}" for key, value in data.items()]
            )
        else:
            try:
                ret_val += str(data)
            except Exception as e:
                # TODO: add logging
                pass

        return ret_val

    @staticmethod
    def serialize(data):
        return PlainTextSerializer.__serialize(data)


serializer2class = {
    'json': JsonSerializer,
    'plain': PlainTextSerializer
}
