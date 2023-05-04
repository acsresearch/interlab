from typing import Any, Union

IntoData = Union[str, "Data", dict, Exception]


# Initially lets just have arbitrary dict
class Data:
    def __init__(self, data: IntoData = None, _type=None, **kwargs):
        assert (data is None) == bool(
            kwargs
        ), "Needs exactly one of `data` or `**kwargs`"
        if data is None:
            data = kwargs

        if isinstance(data, Exception):
            data = dict(text=str(data))
            _type = _type or "error"
        if isinstance(data, str):
            data = dict(text=data)
        if isinstance(data, Data):
            _type = _type or data._type
            data = data.data

        assert isinstance(data, dict)
        self.data = data
        self._type = _type or "default"

    def to_json(self):
        return dict(_type=self._type, **self.data)

    def __getattribute__(self, name: str) -> Any:
        try:
            data = object.__getattribute__(self, "data")
            if name in data:
                return data[name]
        except AttributeError:  # This happens e.g. in copy.copy
            pass
        return object.__getattribute__(self, name)

    def __setattr__(self, name: str, value: Any) -> None:
        try:
            data = object.__getattribute__(self, "data")
            if name in data:
                data[name] = value
        except AttributeError:  # This happens e.g. in the constructor
            pass
        object.__setattr__(self, name, value)
