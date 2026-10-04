# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

from __future__ import annotations

import enum
import functools
import typing

import dsviper

from .. import definitions
from .._codegen import NOT_GIVEN, AnyConceptKey, AnyValue, Key, NotGiven, Proxy, is_known, register, unwrap, wrap
from .._codegen.container import _unwrap_deep

if typing.TYPE_CHECKING:
    from .. import containers

USER: dsviper.ValueUUId = dsviper.ValueUUId.create("bfb135a1-49e6-132a-e693-b84be57e9726")
STATUS: dsviper.ValueUUId = dsviper.ValueUUId.create("38733635-4817-2af4-838c-a0fe77c65e53")
ACCOUNT: dsviper.ValueUUId = dsviper.ValueUUId.create("da60982c-7ae3-6f6f-2052-8cf086fb13dc")
IDENTITY: dsviper.ValueUUId = dsviper.ValueUUId.create("5ff52b96-4e51-7c9b-d934-c542f6ac9255")
LOGIN: dsviper.ValueUUId = dsviper.ValueUUId.create("f223819a-167a-b9f8-e483-3abf4a0c2518")
TEXTURE: dsviper.ValueUUId = dsviper.ValueUUId.create("dc4e365c-5641-2259-3853-65ee1de7ae69")
THUMBNAIL: dsviper.ValueUUId = dsviper.ValueUUId.create("54458468-e1d5-f9f1-b5df-cdf4d5c76cb2")

class UserKey(Key):
    """A user."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def concept(cls) -> dsviper.TypeConcept:
        return definitions().check_concept(USER)

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.Type:
        return dsviper.TypeKey(cls.concept())

    def __init__(self, identifier: dsviper.ValueKey | dsviper.ValueUUId | str | NotGiven = NOT_GIVEN,
                 runtime_id: dsviper.ValueUUId | str | NotGiven = NOT_GIVEN) -> None:
        """No argument gives the invalid key, an instance identifier the key of that instance, an
        instance identifier and a runtime id the key of a concept that is a User or descends
        from it. A key of another concept is converted with its to_parent_key() or
        to_any_concept_key(), and back with from_any_concept_key()."""
        if isinstance(identifier, UserKey):
            raise TypeError(f"{identifier!r} is a Tuto::UserKey already: use it as it is")
        if isinstance(identifier, Proxy):
            raise TypeError(f"{identifier!r} is not a Tuto::UserKey: "
                            "widen it with to_parent_key(), or narrow it with from_any_concept_key()")
        if isinstance(identifier, dsviper.ValueKey):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a key carries its runtime id")
            if identifier.type() != self.type():
                raise TypeError(f"this value is not a Tuto::UserKey: {identifier.detail_type_representation()}")
            super().__init__(identifier)
        elif isinstance(identifier, NotGiven):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a runtime id needs an instance identifier")
            super().__init__(dsviper.ValueKey.create(self.concept(), dsviper.ValueUUId.INVALID))
        elif isinstance(identifier, (dsviper.ValueUUId, str)):
            if isinstance(runtime_id, NotGiven):
                super().__init__(dsviper.ValueKey.create(self.concept(), identifier))
                return
            concept = definitions().check_concept(dsviper.ValueUUId(runtime_id))
            key = dsviper.ValueKey.create(concept, identifier)
            if not key.is_member(self.concept()):
                raise TypeError(f"{concept.representation()} is not a Tuto::User")
            super().__init__(key.to_member_key(self.concept()))
        else:
            raise TypeError(f"{identifier!r} is not an instance identifier")

    @classmethod
    def create(cls) -> UserKey:
        return cls(dsviper.ValueUUId.create())

    def instance_id(self) -> dsviper.ValueUUId:
        return self._value.instance_id()

    def runtime_id(self) -> dsviper.ValueUUId:
        return self._value.type_concept().runtime_id()

    def is_valid(self) -> bool:
        return self._value.instance_id().is_valid()

    def to_any_concept_key(self) -> AnyConceptKey:
        return AnyConceptKey(self._value.to_any_concept_key())

    @classmethod
    def from_any_concept_key(cls, key: AnyConceptKey | Proxy[dsviper.ValueKey] | dsviper.ValueKey) -> UserKey | None:
        value = key._value if isinstance(key, Proxy) else key
        return cls(value.to_member_key(cls.concept())) if value.is_member(cls.concept()) else None

    def description(self) -> str:
        return f"{self._value.instance_id().encoded()}:Tuto::UserKey{self._held()}"

    def is_known(self) -> bool:
        return is_known(self._value)

    def __repr__(self) -> str:
        return self.description()


class Status(enum.Enum):
    """Lifecycle state of a User account."""
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeEnumeration:
        return definitions().check_enumeration(STATUS)

    @classmethod
    def from_str(cls, name: str) -> Status:
        """Return the case the model names `name`, spelled as the DSM spells it:
        `from_str("pending")` is `Status.PENDING`. The member's own name is
        Python's, reached by `Status["PENDING"]`. An unknown name raises ValueError."""
        if not isinstance(name, str):
            raise TypeError(f"{name!r} is not a case name")
        return cls(name)

    @classmethod
    def _missing_(cls, value: object) -> typing.Any:
        if isinstance(value, dsviper.ValueEnumeration):
            if value.type_enumeration() != cls.type():
                raise TypeError(f"{value!r} is not a case of Status")
            return cls(value.name())
        if isinstance(value, int) and not isinstance(value, bool):
            cases = list(cls)
            if value in range(len(cases)):
                return cases[value]
            return None
        if isinstance(value, str):
            return None
        raise TypeError(f"{value!r} is neither a case of Status nor an index")

    def index(self) -> int:
        return list(type(self)).index(self)

    def unwrap_value(self) -> dsviper.ValueEnumeration:
        return dsviper.ValueEnumeration.cast(dsviper.Value.create(type(self).type(), self.value))

    def __lt__(self, other: Status) -> bool:
        if not isinstance(other, Status):
            return NotImplemented
        return bool(self.unwrap_value() < other.unwrap_value())

    def __le__(self, other: Status) -> bool:
        if not isinstance(other, Status):
            return NotImplemented
        return bool(self.unwrap_value() <= other.unwrap_value())

    def __gt__(self, other: Status) -> bool:
        if not isinstance(other, Status):
            return NotImplemented
        return bool(self.unwrap_value() > other.unwrap_value())

    def __ge__(self, other: Status) -> bool:
        if not isinstance(other, Status):
            return NotImplemented
        return bool(self.unwrap_value() >= other.unwrap_value())

    @classmethod
    def wrap_value(cls, value: dsviper.Value) -> Status:
        """The case a Viper value of exactly this enumeration holds; another type raises
        TypeError."""
        if not isinstance(value, dsviper.Value) or value.type() != cls.type():
            raise TypeError(f"this value is not a {cls.type().representation()}")
        return cls(dsviper.ValueEnumeration.cast(value))

    @classmethod
    def _wrap(cls, value: typing.Any) -> Status:
        return cls.wrap_value(value)

    def _unwrap(self) -> str:
        return typing.cast(str, self.value)

class Account(Proxy[dsviper.ValueStructure]):
    """Account state for a User."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(ACCOUNT)

    def __init__(self, source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 state: Status | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        if source is None:
            source = dsviper.ValueStructure(self.type())
        elif isinstance(source, dict):
            source = dsviper.ValueStructure(self.type(), _unwrap_deep(source))
        elif source.type() != self.type():
            raise TypeError("this value is not a Tuto::Account")
        super().__init__(source)
        if not isinstance(state, NotGiven):
            self.state = state

    @property
    def state(self) -> Status:
        return typing.cast("Status", wrap(self._value.at("state", encoded=False)))

    @state.setter
    def state(self, value: Status) -> None:
        self._value.set("state", unwrap(value))

    def __repr__(self) -> str:
        return f"Tuto::Account(state={self.state})"


class Identity(Proxy[dsviper.ValueStructure]):
    """Identity information for a User."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(IDENTITY)

    def __init__(self, source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 firstname: str | NotGiven = NOT_GIVEN,
                 lastname: str | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        if source is None:
            source = dsviper.ValueStructure(self.type())
        elif isinstance(source, dict):
            source = dsviper.ValueStructure(self.type(), _unwrap_deep(source))
        elif source.type() != self.type():
            raise TypeError("this value is not a Tuto::Identity")
        super().__init__(source)
        if not isinstance(firstname, NotGiven):
            self.firstname = firstname
        if not isinstance(lastname, NotGiven):
            self.lastname = lastname

    @property
    def firstname(self) -> str:
        return typing.cast("str", self._value.at("firstname"))

    @firstname.setter
    def firstname(self, value: str) -> None:
        self._value.set("firstname", value)

    @property
    def lastname(self) -> str:
        return typing.cast("str", self._value.at("lastname"))

    @lastname.setter
    def lastname(self, value: str) -> None:
        self._value.set("lastname", value)

    def __repr__(self) -> str:
        return f"Tuto::Identity(firstname={self.firstname}, lastname={self.lastname})"


class Login(Proxy[dsviper.ValueStructure]):
    """Login credentials for a User."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(LOGIN)

    def __init__(self, source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 nickname: str | NotGiven = NOT_GIVEN,
                 password: str | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        if source is None:
            source = dsviper.ValueStructure(self.type())
        elif isinstance(source, dict):
            source = dsviper.ValueStructure(self.type(), _unwrap_deep(source))
        elif source.type() != self.type():
            raise TypeError("this value is not a Tuto::Login")
        super().__init__(source)
        if not isinstance(nickname, NotGiven):
            self.nickname = nickname
        if not isinstance(password, NotGiven):
            self.password = password

    @property
    def nickname(self) -> str:
        return typing.cast("str", self._value.at("nickname"))

    @nickname.setter
    def nickname(self, value: str) -> None:
        self._value.set("nickname", value)

    @property
    def password(self) -> str:
        return typing.cast("str", self._value.at("password"))

    @password.setter
    def password(self, value: str) -> None:
        self._value.set("password", value)

    def __repr__(self) -> str:
        return f"Tuto::Login(nickname={self.nickname}, password={self.password})"


class Texture(Proxy[dsviper.ValueStructure]):
    """A high-resolution texture stored by reference."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(TEXTURE)

    def __init__(self, source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 width: int | NotGiven = NOT_GIVEN,
                 height: int | NotGiven = NOT_GIVEN,
                 pixels: dsviper.ValueBlobId | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        if source is None:
            source = dsviper.ValueStructure(self.type())
        elif isinstance(source, dict):
            source = dsviper.ValueStructure(self.type(), _unwrap_deep(source))
        elif source.type() != self.type():
            raise TypeError("this value is not a Tuto::Texture")
        super().__init__(source)
        if not isinstance(width, NotGiven):
            self.width = width
        if not isinstance(height, NotGiven):
            self.height = height
        if not isinstance(pixels, NotGiven):
            self.pixels = pixels

    @property
    def width(self) -> int:
        return typing.cast("int", self._value.at("width"))

    @width.setter
    def width(self, value: int) -> None:
        self._value.set("width", value)

    @property
    def height(self) -> int:
        return typing.cast("int", self._value.at("height"))

    @height.setter
    def height(self, value: int) -> None:
        self._value.set("height", value)

    @property
    def pixels(self) -> dsviper.ValueBlobId:
        return typing.cast("dsviper.ValueBlobId", self._value.at("pixels"))

    @pixels.setter
    def pixels(self, value: dsviper.ValueBlobId) -> None:
        self._value.set("pixels", value)

    def __repr__(self) -> str:
        return f"Tuto::Texture(width={self.width}, height={self.height}, pixels={self.pixels})"


class Thumbnail(Proxy[dsviper.ValueStructure]):
    """A small avatar image stored inline."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(THUMBNAIL)

    def __init__(self, source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 width: int | NotGiven = NOT_GIVEN,
                 height: int | NotGiven = NOT_GIVEN,
                 data: dsviper.ValueBlob | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        if source is None:
            source = dsviper.ValueStructure(self.type())
        elif isinstance(source, dict):
            source = dsviper.ValueStructure(self.type(), _unwrap_deep(source))
        elif source.type() != self.type():
            raise TypeError("this value is not a Tuto::Thumbnail")
        super().__init__(source)
        if not isinstance(width, NotGiven):
            self.width = width
        if not isinstance(height, NotGiven):
            self.height = height
        if not isinstance(data, NotGiven):
            self.data = data

    @property
    def width(self) -> int:
        return typing.cast("int", self._value.at("width"))

    @width.setter
    def width(self, value: int) -> None:
        self._value.set("width", value)

    @property
    def height(self) -> int:
        return typing.cast("int", self._value.at("height"))

    @height.setter
    def height(self, value: int) -> None:
        self._value.set("height", value)

    @property
    def data(self) -> dsviper.ValueBlob:
        return typing.cast("dsviper.ValueBlob", self._value.at("data"))

    @data.setter
    def data(self, value: dsviper.ValueBlob) -> None:
        self._value.set("data", value)

    def __repr__(self) -> str:
        return f"Tuto::Thumbnail(width={self.width}, height={self.height}, data={self.data})"


register({USER: UserKey, STATUS: Status, ACCOUNT: Account, IDENTITY: Identity, LOGIN: Login, TEXTURE: Texture, THUMBNAIL: Thumbnail})

__all__ = ["UserKey", "Status", "Account", "Identity", "Login", "Texture", "Thumbnail", "USER", "STATUS", "ACCOUNT", "IDENTITY", "LOGIN", "TEXTURE", "THUMBNAIL"]
