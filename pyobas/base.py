import copy
import importlib
import json
import pprint
import textwrap
from types import ModuleType
from typing import TYPE_CHECKING, Any, Dict, Iterable, Optional, Type, Union

from pyobas.exceptions import OpenBASParsingError

from . import utils
from .client import OpenBAS, OpenBASList

__all__ = [
    "RESTObject",
    "RESTObjectList",
    "RESTManager",
]


class RESTObject:
    _id_attr: Optional[str] = "id"
    _attrs: Dict[str, Any]
    _created_from_list: bool  # Indicates if object was created from a list() action
    _module: ModuleType
    _parent_attrs: Dict[str, Any]
    _repr_attr: Optional[str] = None
    _updated_attrs: Dict[str, Any]
    manager: "RESTManager"

    def __init__(
        self,
        manager: "RESTManager",
        attrs: Dict[str, Any],
        *,
        created_from_list: bool = False,
    ) -> None:
        if not isinstance(attrs, dict):
            raise OpenBASParsingError(
                f"Attempted to initialize RESTObject with a non-dictionary value: "
                f"{attrs!r}\nThis likely indicates an incorrect or malformed server "
                f"response."
            )
        self.__dict__.update(
            {
                "manager": manager,
                "_attrs": attrs,
                "_updated_attrs": {},
                "_module": importlib.import_module(self.__module__),
                "_created_from_list": created_from_list,
            }
        )
        self.__dict__["_parent_attrs"] = self.manager.parent_attrs
        self._create_managers()

    def __getstate__(self) -> Dict[str, Any]:
        state = self.__dict__.copy()
        module = state.pop("_module")
        state["_module_name"] = module.__name__
        return state

    def __setstate__(self, state: Dict[str, Any]) -> None:
        module_name = state.pop("_module_name")
        self.__dict__.update(state)
        self.__dict__["_module"] = importlib.import_module(module_name)

    def __getattr__(self, name: str) -> Any:
        if name in self.__dict__["_updated_attrs"]:
            return self.__dict__["_updated_attrs"][name]

        if name in self.__dict__["_attrs"]:
            value = self.__dict__["_attrs"][name]
            if isinstance(value, list):
                self.__dict__["_updated_attrs"][name] = value[:]
                return self.__dict__["_updated_attrs"][name]

            return value

        if name in self.__dict__["_parent_attrs"]:
            return self.__dict__["_parent_attrs"][name]

        message = f"{type(self).__name__!r} object has no attribute {name!r}"
        if self._created_from_list:
            message = f"{message}\n\n" + textwrap.fill(
                f"{self.__class__!r} was created via a list() call and "
                f"only a subset of the data may be present. To ensure "
                f"all data is present get the object using a "
                f"get(object.id) call. For more details, see:"
            )
        raise AttributeError(message)

    def __setattr__(self, name: str, value: Any) -> None:
        self.__dict__["_updated_attrs"][name] = value

    def asdict(self, *, with_parent_attrs: bool = False) -> Dict[str, Any]:
        data = {}
        if with_parent_attrs:
            data.update(copy.deepcopy(self._parent_attrs))
        data.update(copy.deepcopy(self._attrs))
        data.update(copy.deepcopy(self._updated_attrs))
        return data

    @property
    def attributes(self) -> Dict[str, Any]:
        return self.asdict(with_parent_attrs=True)

    def to_json(self, *, with_parent_attrs: bool = False, **kwargs: Any) -> str:
        return json.dumps(self.asdict(with_parent_attrs=with_parent_attrs), **kwargs)

    def __str__(self) -> str:
        return f"{type(self)} => {self.asdict()}"

    def pformat(self) -> str:
        return f"{type(self)} => \n{pprint.pformat(self.asdict())}"

    def pprint(self) -> None:
        print(self.pformat())

    def __repr__(self) -> str:
        name = self.__class__.__name__

        if (self._id_attr and self._repr_value) and (self._id_attr != self._repr_attr):
            return (
                f"<{name} {self._id_attr}:{self.get_id()} "
                f"{self._repr_attr}:{self._repr_value}>"
            )
        if self._id_attr:
            return f"<{name} {self._id_attr}:{self.get_id()}>"
        if self._repr_value:
            return f"<{name} {self._repr_attr}:{self._repr_value}>"

        return f"<{name}>"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, RESTObject):
            return NotImplemented
        if self.get_id() and other.get_id():
            return self.get_id() == other.get_id()
        return super() == other

    def __ne__(self, other: object) -> bool:
        if not isinstance(other, RESTObject):
            return NotImplemented
        if self.get_id() and other.get_id():
            return self.get_id() != other.get_id()
        return super() != other

    def __dir__(self) -> Iterable[str]:
        return set(self.attributes).union(super().__dir__())

    def __hash__(self) -> int:
        if not self.get_id():
            return super().__hash__()
        return hash(self.get_id())

    def _create_managers(self) -> None:
        # NOTE(jlvillal): We are creating our managers by looking at the class
        # annotations. If an attribute is annotated as being a *Manager type
        # then we create the manager and assign it to the attribute.
        for attr, annotation in sorted(self.__annotations__.items()):
            # We ignore creating a manager for the 'manager' attribute as that
            # is done in the self.__init__() method
            if attr in ("manager",):
                continue
            if not isinstance(annotation, (type, str)):
                continue
            if isinstance(annotation, type):
                cls_name = annotation.__name__
            else:
                cls_name = annotation
            # All *Manager classes are used except for the base "RESTManager" class
            if cls_name == "RESTManager" or not cls_name.endswith("Manager"):
                continue
            cls = getattr(self._module, cls_name)
            manager = cls(self.manager.openbas, parent=self)
            # Since we have our own __setattr__ method, we can't use setattr()
            self.__dict__[attr] = manager

    def _update_attrs(self, new_attrs: Dict[str, Any]) -> None:
        self.__dict__["_updated_attrs"] = {}
        self.__dict__["_attrs"] = new_attrs

    def get_id(self) -> Optional[Union[int, str]]:
        """Returns the id of the resource."""
        if self._id_attr is None or not hasattr(self, self._id_attr):
            return None
        id_val = getattr(self, self._id_attr)
        if TYPE_CHECKING:
            assert id_val is None or isinstance(id_val, (int, str))
        return id_val

    @property
    def _repr_value(self) -> Optional[str]:
        """Safely returns the human-readable resource name if present."""
        if self._repr_attr is None or not hasattr(self, self._repr_attr):
            return None
        repr_val = getattr(self, self._repr_attr)
        if TYPE_CHECKING:
            assert isinstance(repr_val, str)
        return repr_val

    @property
    def encoded_id(self) -> Optional[Union[int, str]]:
        """Ensure that the ID is url-encoded so that it can be safely used in a URL
        path"""
        obj_id = self.get_id()
        if isinstance(obj_id, str):
            obj_id = utils.EncodedId(obj_id)
        return obj_id


class RESTObjectList:
    def __init__(
        self, manager: "RESTManager", obj_cls: Type[RESTObject], _list: OpenBASList
    ) -> None:
        self.manager = manager
        self._obj_cls = obj_cls
        self._list = _list

    def __iter__(self) -> "RESTObjectList":
        return self

    def __len__(self) -> int:
        return len(self._list)

    def __next__(self) -> RESTObject:
        return self.next()

    def next(self) -> RESTObject:
        data = self._list.next()
        return self._obj_cls(self.manager, data, created_from_list=True)

    @property
    def current_page(self) -> int:
        """The current page number."""
        return self._list.current_page

    @property
    def prev_page(self) -> Optional[int]:
        """The previous page number.

        If None, the current page is the first.
        """
        return self._list.prev_page

    @property
    def next_page(self) -> Optional[int]:
        """The next page number.

        If None, the current page is the last.
        """
        return self._list.next_page

    @property
    def per_page(self) -> Optional[int]:
        """The number of items per page."""
        return self._list.per_page

    @property
    def total_pages(self) -> Optional[int]:
        """The total number of pages."""
        return self._list.total_pages

    @property
    def total(self) -> Optional[int]:
        """The total number of items."""
        return self._list.total


class RESTManager:
    """Base class for CRUD operations on objects.

    Derived class must define ``_path`` and ``_obj_cls``.

    ``_path``: Base URL path on which requests will be sent (e.g. '/projects')
    ``_obj_cls``: The class of objects that will be created
    """

    _create_attrs: Any
    _update_attrs: Any
    _path: Optional[str] = None
    _obj_cls: Optional[Type[RESTObject]] = None
    _from_parent_attrs: Dict[str, Any] = {}
    _types: Dict[str, Any] = {}

    _computed_path: Optional[str]
    _parent: Optional[RESTObject]
    _parent_attrs: Dict[str, Any]
    openbas: OpenBAS

    def __init__(self, openbas: OpenBAS, parent: Optional[RESTObject] = None) -> None:
        self.openbas = openbas
        self._parent = parent  # for nested managers
        self._computed_path = self._compute_path()

    @property
    def parent_attrs(self) -> Optional[Dict[str, Any]]:
        return self._parent_attrs

    def _compute_path(self, path: Optional[str] = None) -> Optional[str]:
        self._parent_attrs = {}
        if path is None:
            path = self._path
        if path is None:
            return None
        if self._parent is None or not self._from_parent_attrs:
            return path

        data: Dict[str, Optional[utils.EncodedId]] = {}
        for self_attr, parent_attr in self._from_parent_attrs.items():
            if not hasattr(self._parent, parent_attr):
                data[self_attr] = None
                continue
            data[self_attr] = utils.EncodedId(getattr(self._parent, parent_attr))
        self._parent_attrs = data
        return path.format(**data)

    @property
    def path(self) -> Optional[str]:
        return self._computed_path
