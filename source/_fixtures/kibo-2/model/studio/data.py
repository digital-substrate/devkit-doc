# Generated from model.dsm.json by kibo-2.0.2.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.3 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

from __future__ import annotations

import builtins as _builtins
import enum
import functools
import typing

import dsviper

from .. import definitions
from .._codegen import NOT_GIVEN, AnyConceptKey, AnyValue, Key, NotGiven, Proxy, is_known, register, unwrap, wrap
from .._codegen import NotGiven as _NotGiven
from .._codegen.container import _init_structure

if typing.TYPE_CHECKING:
    from .. import containers

DEVICE: dsviper.ValueUUId = dsviper.ValueUUId.create("8683b723-08d0-2226-df1a-bc67b70af4ee")
MEMBER: dsviper.ValueUUId = dsviper.ValueUUId.create("574e1099-99ec-b26a-058c-38ae940058c7")
ADMIN: dsviper.ValueUUId = dsviper.ValueUUId.create("694a5e25-e0f1-26bc-aa65-26f83050b149")
PRINCIPAL: dsviper.ValueUUId = dsviper.ValueUUId.create("80d2180b-4a07-20dc-406a-ecc529fe6c84")
CREDENTIALS: dsviper.ValueUUId = dsviper.ValueUUId.create("373aa361-d7fe-70b0-ccb7-21da63ec7383")
NAME: dsviper.ValueUUId = dsviper.ValueUUId.create("c50f8f68-02b8-e93f-b779-08a9e001635f")
PROFILE: dsviper.ValueUUId = dsviper.ValueUUId.create("1fc147aa-9492-4864-d4aa-c355f051aa11")

class DeviceKey(Key):
    """A device a member signs in from."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def concept(cls) -> dsviper.TypeConcept:
        return definitions().check_concept(DEVICE)

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.Type:
        return dsviper.TypeKey(cls.concept())

    def __init__(self, identifier: dsviper.ValueKey | dsviper.ValueUUId | str | NotGiven = NOT_GIVEN,
                 runtime_id: dsviper.ValueUUId | str | NotGiven = NOT_GIVEN) -> None:
        """No argument gives the invalid key, an instance identifier the key of that instance, an
        instance identifier and a runtime id the key of a concept that is a Device or descends
        from it. A key of another concept is converted with its to_parent_key() or
        to_any_concept_key(), and back with from_any_concept_key()."""
        if isinstance(identifier, DeviceKey):
            raise TypeError(f"{identifier!r} is a Studio::DeviceKey already: use it as it is")
        if isinstance(identifier, Proxy):
            raise TypeError(f"{identifier!r} is not a Studio::DeviceKey: "
                            "widen it with to_parent_key(), or narrow it with from_any_concept_key()")
        if isinstance(identifier, dsviper.ValueKey):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a key carries its runtime id")
            if identifier.type() != self.type():
                raise TypeError(f"this value is not a Studio::DeviceKey: {identifier.detail_type_representation()}")
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
                raise TypeError(f"{concept.representation()} is not a Studio::Device")
            super().__init__(key.to_member_key(self.concept()))
        else:
            raise TypeError(f"{identifier!r} is not an instance identifier")

    @classmethod
    def create(cls) -> DeviceKey:
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
    def from_any_concept_key(cls, key: AnyConceptKey | Proxy[dsviper.ValueKey] | dsviper.ValueKey) -> DeviceKey | None:
        value = key._value if isinstance(key, Proxy) else key
        return cls(value.to_member_key(cls.concept())) if value.is_member(cls.concept()) else None

    def description(self) -> str:
        return f"{self._value.instance_id().encoded()}:Studio::DeviceKey{self._held()}"

    def is_known(self) -> bool:
        return is_known(self._value)

    def __repr__(self) -> str:
        return self.description()



class MemberKey(Key):
    """A member of the studio."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def concept(cls) -> dsviper.TypeConcept:
        return definitions().check_concept(MEMBER)

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.Type:
        return dsviper.TypeKey(cls.concept())

    def __init__(self, identifier: dsviper.ValueKey | dsviper.ValueUUId | str | NotGiven = NOT_GIVEN,
                 runtime_id: dsviper.ValueUUId | str | NotGiven = NOT_GIVEN) -> None:
        """No argument gives the invalid key, an instance identifier the key of that instance, an
        instance identifier and a runtime id the key of a concept that is a Member or descends
        from it. A key of another concept is converted with its to_parent_key() or
        to_any_concept_key(), and back with from_any_concept_key()."""
        if isinstance(identifier, MemberKey):
            raise TypeError(f"{identifier!r} is a Studio::MemberKey already: use it as it is")
        if isinstance(identifier, Proxy):
            raise TypeError(f"{identifier!r} is not a Studio::MemberKey: "
                            "widen it with to_parent_key(), or narrow it with from_any_concept_key()")
        if isinstance(identifier, dsviper.ValueKey):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a key carries its runtime id")
            if identifier.type() != self.type():
                raise TypeError(f"this value is not a Studio::MemberKey: {identifier.detail_type_representation()}")
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
                raise TypeError(f"{concept.representation()} is not a Studio::Member")
            super().__init__(key.to_member_key(self.concept()))
        else:
            raise TypeError(f"{identifier!r} is not an instance identifier")

    @classmethod
    def create(cls) -> MemberKey:
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
    def from_any_concept_key(cls, key: AnyConceptKey | Proxy[dsviper.ValueKey] | dsviper.ValueKey) -> MemberKey | None:
        value = key._value if isinstance(key, Proxy) else key
        return cls(value.to_member_key(cls.concept())) if value.is_member(cls.concept()) else None

    def description(self) -> str:
        return f"{self._value.instance_id().encoded()}:Studio::MemberKey{self._held()}"

    def is_known(self) -> bool:
        return is_known(self._value)

    def __repr__(self) -> str:
        return self.description()

    def to_admin_key(self) -> AdminKey | None:
        return AdminKey.from_any_concept_key(self)

    @classmethod
    def from_admin_key(cls, key: AdminKey) -> MemberKey:
        if not isinstance(key, AdminKey):
            raise TypeError(f"{key!r} is not a AdminKey")
        return cls(key._value.to_member_key(cls.concept()))


class AdminKey(Key):
    """A member who administers the others."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def concept(cls) -> dsviper.TypeConcept:
        return definitions().check_concept(ADMIN)

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.Type:
        return dsviper.TypeKey(cls.concept())

    def __init__(self, identifier: dsviper.ValueKey | dsviper.ValueUUId | str | NotGiven = NOT_GIVEN,
                 runtime_id: dsviper.ValueUUId | str | NotGiven = NOT_GIVEN) -> None:
        """No argument gives the invalid key, an instance identifier the key of that instance, an
        instance identifier and a runtime id the key of a concept that is a Admin or descends
        from it. A key of another concept is converted with its to_parent_key() or
        to_any_concept_key(), and back with from_any_concept_key()."""
        if isinstance(identifier, AdminKey):
            raise TypeError(f"{identifier!r} is a Studio::AdminKey already: use it as it is")
        if isinstance(identifier, Proxy):
            raise TypeError(f"{identifier!r} is not a Studio::AdminKey: "
                            "widen it with to_parent_key(), or narrow it with from_any_concept_key()")
        if isinstance(identifier, dsviper.ValueKey):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a key carries its runtime id")
            if identifier.type() != self.type():
                raise TypeError(f"this value is not a Studio::AdminKey: {identifier.detail_type_representation()}")
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
                raise TypeError(f"{concept.representation()} is not a Studio::Admin")
            super().__init__(key.to_member_key(self.concept()))
        else:
            raise TypeError(f"{identifier!r} is not an instance identifier")

    @classmethod
    def create(cls) -> AdminKey:
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
    def from_any_concept_key(cls, key: AnyConceptKey | Proxy[dsviper.ValueKey] | dsviper.ValueKey) -> AdminKey | None:
        value = key._value if isinstance(key, Proxy) else key
        return cls(value.to_member_key(cls.concept())) if value.is_member(cls.concept()) else None

    def description(self) -> str:
        return f"{self._value.instance_id().encoded()}:Studio::AdminKey{self._held()}"

    def is_known(self) -> bool:
        return is_known(self._value)

    def __repr__(self) -> str:
        return self.description()

    def to_parent_key(self) -> MemberKey:
        return MemberKey(self._value.to_parent_key())


class PrincipalKey(Key):
    """Anything that signs in: a member or a device."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def club(cls) -> dsviper.TypeClub:
        return definitions().check_club(PRINCIPAL)

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.Type:
        return dsviper.TypeKey(cls.club())

    def __init__(self, key: PrincipalKey | DeviceKey | MemberKey | dsviper.ValueKey | dsviper.ValueUUId | str | NotGiven = NOT_GIVEN,
                 runtime_id: dsviper.ValueUUId | str | NotGiven = NOT_GIVEN) -> None:
        """No argument gives the invalid key; else a key of a member, or an instance identifier
        and the runtime id of a member."""
        if isinstance(key, NotGiven):
            if not isinstance(runtime_id, NotGiven):
                raise TypeError("a runtime id needs an instance identifier")
            super().__init__(dsviper.ValueKey.cast(dsviper.Value.create(self.type())))
            return
        if isinstance(key, (dsviper.ValueUUId, str)):
            if isinstance(runtime_id, NotGiven):
                raise TypeError("an instance identifier needs the runtime id of a member of Studio::Principal")
            key = dsviper.ValueKey.create(definitions().check_concept(dsviper.ValueUUId(runtime_id)), key)
        elif not isinstance(runtime_id, NotGiven):
            raise TypeError("a key carries its runtime id")
        value = key._value if isinstance(key, Proxy) else key
        if not isinstance(value, dsviper.ValueKey):
            raise TypeError("this value is not a key")
        if value.type() == self.type():
            super().__init__(value)
            return
        if not self._designates_member(value.type_concept()):
            raise TypeError("this key does not designate a member of Studio::Principal")
        super().__init__(value.to_club_key(self.club()))

    def instance_id(self) -> dsviper.ValueUUId:
        return self._value.instance_id()

    def runtime_id(self) -> dsviper.ValueUUId:
        return self._value.type_concept().runtime_id()

    def is_valid(self) -> bool:
        return self._value.instance_id().is_valid()

    def to_any_concept_key(self) -> AnyConceptKey:
        return AnyConceptKey(self._value.to_any_concept_key())

    @classmethod
    def from_any_concept_key(cls, key: AnyConceptKey | Proxy[dsviper.ValueKey] | dsviper.ValueKey) -> PrincipalKey | None:
        value = key._value if isinstance(key, Proxy) else key
        return cls(value) if cls._designates_member(value.type_concept()) else None

    @classmethod
    def _designates_member(cls, concept: dsviper.TypeConcept) -> bool:
        return any(concept.is_member(member) for member in cls.club().members())

    def description(self) -> str:
        return f"{self._value.instance_id().encoded()}:Studio::PrincipalKey{self._held()}"

    def is_known(self) -> bool:
        return is_known(self._value)

    @classmethod
    def from_device_key(cls, key: DeviceKey) -> PrincipalKey:
        return cls(key)

    @classmethod
    def from_member_key(cls, key: MemberKey) -> PrincipalKey:
        return cls(key)

    def to_device_key(self) -> DeviceKey | None:
        return DeviceKey.from_any_concept_key(self)

    def to_member_key(self) -> MemberKey | None:
        return MemberKey.from_any_concept_key(self)

    def __repr__(self) -> str:
        return self.description()

class Credentials(Proxy[dsviper.ValueStructure]):
    """What a principal signs in with."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(CREDENTIALS)

    def __init__(_self, _source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 login: str | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        _init_structure(_self, _self.type(), _source, "Studio::Credentials")
        if not _builtins.isinstance(login, _NotGiven):
            _self.login = login

    @property
    def login(self) -> str:
        return typing.cast("str", self._value.at("login"))

    @login.setter
    def login(self, value: str) -> None:
        self._value.set("login", value)

    def __repr__(self) -> str:
        return f"Studio::Credentials(login={self.login})"


class Name(Proxy[dsviper.ValueStructure]):
    """A name, as a member gives it."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(NAME)

    def __init__(_self, _source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 first: str | NotGiven = NOT_GIVEN,
                 last: str | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        _init_structure(_self, _self.type(), _source, "Studio::Name")
        if not _builtins.isinstance(first, _NotGiven):
            _self.first = first
        if not _builtins.isinstance(last, _NotGiven):
            _self.last = last

    @property
    def first(self) -> str:
        return typing.cast("str", self._value.at("first"))

    @first.setter
    def first(self, value: str) -> None:
        self._value.set("first", value)

    @property
    def last(self) -> str:
        return typing.cast("str", self._value.at("last"))

    @last.setter
    def last(self, value: str) -> None:
        self._value.set("last", value)

    def __repr__(self) -> str:
        return f"Studio::Name(first={self.first}, last={self.last})"


class Profile(Proxy[dsviper.ValueStructure]):
    """How a member presents itself."""
    __slots__ = ()

    @classmethod
    @functools.cache
    def type(cls) -> dsviper.TypeStructure:
        return definitions().check_structure(PROFILE)

    def __init__(_self, _source: dsviper.ValueStructure | dict[str, typing.Any] | None = None, /, *,
                 name: Name | NotGiven = NOT_GIVEN,
                 tags: containers.Vector_of_string | typing.Sequence[str] | NotGiven = NOT_GIVEN,
                 roles: containers.Set_of_string | typing.Iterable[str] | NotGiven = NOT_GIVEN,
                 settings: containers.Map_of_string_to_string | dict[str, str] | NotGiven = NOT_GIVEN,
                 motto: containers.Optional_of_string | str | None | NotGiven = NOT_GIVEN,
                 level: int | NotGiven = NOT_GIVEN) -> None:
        """Fields by keyword, in snake_case; or a source: a Viper ValueStructure of this
        type, boxed and not copied, or a dict keyed by the DSM field names, as the runtime
        takes it."""
        _init_structure(_self, _self.type(), _source, "Studio::Profile")
        if not _builtins.isinstance(name, _NotGiven):
            _self.name = name
        if not _builtins.isinstance(tags, _NotGiven):
            _self.tags = tags
        if not _builtins.isinstance(roles, _NotGiven):
            _self.roles = roles
        if not _builtins.isinstance(settings, _NotGiven):
            _self.settings = settings
        if not _builtins.isinstance(motto, _NotGiven):
            _self.motto = motto
        if not _builtins.isinstance(level, _NotGiven):
            _self.level = level

    @property
    def name(self) -> Name:
        return typing.cast("Name", wrap(self._value.at("name", encoded=False)))

    @name.setter
    def name(self, value: Name) -> None:
        self._value.set("name", unwrap(value))

    @property
    def tags(self) -> containers.Vector_of_string:
        return typing.cast("containers.Vector_of_string", wrap(self._value.at("tags", encoded=False)))

    @tags.setter
    def tags(self, value: containers.Vector_of_string | typing.Sequence[str]) -> None:
        self._value.set("tags", unwrap(value))

    @property
    def roles(self) -> containers.Set_of_string:
        return typing.cast("containers.Set_of_string", wrap(self._value.at("roles", encoded=False)))

    @roles.setter
    def roles(self, value: containers.Set_of_string | typing.Iterable[str]) -> None:
        self._value.set("roles", unwrap(value))

    @property
    def settings(self) -> containers.Map_of_string_to_string:
        return typing.cast("containers.Map_of_string_to_string", wrap(self._value.at("settings", encoded=False)))

    @settings.setter
    def settings(self, value: containers.Map_of_string_to_string | dict[str, str]) -> None:
        self._value.set("settings", unwrap(value))

    @property
    def motto(self) -> containers.Optional_of_string:
        return typing.cast("containers.Optional_of_string", wrap(self._value.at("motto", encoded=False)))

    @motto.setter
    def motto(self, value: containers.Optional_of_string | str | None) -> None:
        self._value.set("motto", unwrap(value))

    @property
    def level(self) -> int:
        return typing.cast("int", self._value.at("level"))

    @level.setter
    def level(self, value: int) -> None:
        self._value.set("level", value)

    def __repr__(self) -> str:
        return f"Studio::Profile(name={self.name}, tags={self.tags}, roles={self.roles}, settings={self.settings}, motto={self.motto}, level={self.level})"


register({DEVICE: DeviceKey, MEMBER: MemberKey, ADMIN: AdminKey, PRINCIPAL: PrincipalKey, CREDENTIALS: Credentials, NAME: Name, PROFILE: Profile})

__all__ = ["DeviceKey", "MemberKey", "AdminKey", "PrincipalKey", "Credentials", "Name", "Profile", "DEVICE", "MEMBER", "ADMIN", "PRINCIPAL", "CREDENTIALS", "NAME", "PROFILE"]
