# Generated from model.dsm.json by kibo-2.0.2.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.3 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

from __future__ import annotations

import functools
import typing

import dsviper

from . import definitions
from ._codegen import AnyValue, Declared, Fixed, Mapping, Matrix, Optional, Ordered, SetView, Variant, Vector, declare

if typing.TYPE_CHECKING:
    from . import containers
    from ._codegen import AnyConceptKey

__all__ = [
    "Optional_of_AnyConceptKey",
    "Optional_of_string",
    "Optional_of_Studio_AdminKey",
    "Optional_of_Studio_Credentials",
    "Optional_of_Studio_DeviceKey",
    "Optional_of_Studio_MemberKey",
    "Optional_of_Studio_PrincipalKey",
    "Optional_of_Studio_Profile",
    "Optional_of_Tuto_Account",
    "Optional_of_Tuto_Identity",
    "Optional_of_Tuto_Login",
    "Optional_of_Tuto_Texture",
    "Optional_of_Tuto_Thumbnail",
    "Optional_of_Tuto_UserKey",
    "Vector_of_string",
    "Set_of_string",
    "Set_of_Studio_MemberKey",
    "Set_of_Studio_PrincipalKey",
    "Set_of_Tuto_UserKey",
    "Map_of_string_to_string",
]

def _type_bool() -> dsviper.TypeBool: return dsviper.TypeBool()
def _type_uint8() -> dsviper.TypeUInt8: return dsviper.TypeUInt8()
def _type_uint16() -> dsviper.TypeUInt16: return dsviper.TypeUInt16()
def _type_uint32() -> dsviper.TypeUInt32: return dsviper.TypeUInt32()
def _type_uint64() -> dsviper.TypeUInt64: return dsviper.TypeUInt64()
def _type_int8() -> dsviper.TypeInt8: return dsviper.TypeInt8()
def _type_int16() -> dsviper.TypeInt16: return dsviper.TypeInt16()
def _type_int32() -> dsviper.TypeInt32: return dsviper.TypeInt32()
def _type_int64() -> dsviper.TypeInt64: return dsviper.TypeInt64()
def _type_float() -> dsviper.TypeFloat: return dsviper.TypeFloat()
def _type_double() -> dsviper.TypeDouble: return dsviper.TypeDouble()
def _type_string() -> dsviper.TypeString: return dsviper.TypeString()
def _type_blob() -> dsviper.TypeBlob: return dsviper.TypeBlob()
def _type_blob_id() -> dsviper.TypeBlobId: return dsviper.TypeBlobId()
def _type_commit_id() -> dsviper.TypeCommitId: return dsviper.TypeCommitId()
def _type_uuid() -> dsviper.TypeUUId: return dsviper.TypeUUId()
def _type_any() -> dsviper.TypeAny: return dsviper.TypeAny()
def _type_AnyConceptKey() -> dsviper.TypeKey: return dsviper.TypeKey(dsviper.TypeAnyConcept())
def _type_Tuto_UserKey() -> dsviper.Type: return dsviper.TypeKey(definitions().check_concept(tuto.data.USER))
def _type_Tuto_Status() -> dsviper.Type: return definitions().check_enumeration(tuto.data.STATUS)
def _type_Tuto_Account() -> dsviper.Type: return definitions().check_structure(tuto.data.ACCOUNT)
def _type_Tuto_Identity() -> dsviper.Type: return definitions().check_structure(tuto.data.IDENTITY)
def _type_Tuto_Login() -> dsviper.Type: return definitions().check_structure(tuto.data.LOGIN)
def _type_Tuto_Texture() -> dsviper.Type: return definitions().check_structure(tuto.data.TEXTURE)
def _type_Tuto_Thumbnail() -> dsviper.Type: return definitions().check_structure(tuto.data.THUMBNAIL)
def _type_Studio_DeviceKey() -> dsviper.Type: return dsviper.TypeKey(definitions().check_concept(studio.data.DEVICE))
def _type_Studio_MemberKey() -> dsviper.Type: return dsviper.TypeKey(definitions().check_concept(studio.data.MEMBER))
def _type_Studio_AdminKey() -> dsviper.Type: return dsviper.TypeKey(definitions().check_concept(studio.data.ADMIN))
def _type_Studio_PrincipalKey() -> dsviper.Type: return dsviper.TypeKey(definitions().check_club(studio.data.PRINCIPAL))
def _type_Studio_Credentials() -> dsviper.Type: return definitions().check_structure(studio.data.CREDENTIALS)
def _type_Studio_Name() -> dsviper.Type: return definitions().check_structure(studio.data.NAME)
def _type_Studio_Profile() -> dsviper.Type: return definitions().check_structure(studio.data.PROFILE)

@functools.cache
def _type_optional_AnyConceptKey() -> dsviper.Type: return dsviper.TypeOptional(_type_AnyConceptKey())
@functools.cache
def _type_optional_string() -> dsviper.Type: return dsviper.TypeOptional(_type_string())
@functools.cache
def _type_optional_Studio_AdminKey() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_AdminKey())
@functools.cache
def _type_optional_Studio_Credentials() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_Credentials())
@functools.cache
def _type_optional_Studio_DeviceKey() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_DeviceKey())
@functools.cache
def _type_optional_Studio_MemberKey() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_MemberKey())
@functools.cache
def _type_optional_Studio_PrincipalKey() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_PrincipalKey())
@functools.cache
def _type_optional_Studio_Profile() -> dsviper.Type: return dsviper.TypeOptional(_type_Studio_Profile())
@functools.cache
def _type_optional_Tuto_Account() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_Account())
@functools.cache
def _type_optional_Tuto_Identity() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_Identity())
@functools.cache
def _type_optional_Tuto_Login() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_Login())
@functools.cache
def _type_optional_Tuto_Texture() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_Texture())
@functools.cache
def _type_optional_Tuto_Thumbnail() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_Thumbnail())
@functools.cache
def _type_optional_Tuto_UserKey() -> dsviper.Type: return dsviper.TypeOptional(_type_Tuto_UserKey())
@functools.cache
def _type_vector_string() -> dsviper.Type: return dsviper.TypeVector(_type_string())
@functools.cache
def _type_set_string() -> dsviper.Type: return dsviper.TypeSet(_type_string())
@functools.cache
def _type_set_Studio_MemberKey() -> dsviper.Type: return dsviper.TypeSet(_type_Studio_MemberKey())
@functools.cache
def _type_set_Studio_PrincipalKey() -> dsviper.Type: return dsviper.TypeSet(_type_Studio_PrincipalKey())
@functools.cache
def _type_set_Tuto_UserKey() -> dsviper.Type: return dsviper.TypeSet(_type_Tuto_UserKey())
@functools.cache
def _type_map_string_to_string() -> dsviper.Type: return dsviper.TypeMap(_type_string(), _type_string())

class Optional_of_AnyConceptKey(Declared, Optional["AnyConceptKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_AnyConceptKey | dsviper.ValueOptional | AnyConceptKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_AnyConceptKey()

class Optional_of_string(Declared, Optional["str"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_string | dsviper.ValueOptional | str | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_string()

class Optional_of_Studio_AdminKey(Declared, Optional["studio.AdminKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_AdminKey | dsviper.ValueOptional | studio.AdminKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_AdminKey()

class Optional_of_Studio_Credentials(Declared, Optional["studio.Credentials"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_Credentials | dsviper.ValueOptional | studio.Credentials | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_Credentials()

class Optional_of_Studio_DeviceKey(Declared, Optional["studio.DeviceKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_DeviceKey | dsviper.ValueOptional | studio.DeviceKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_DeviceKey()

class Optional_of_Studio_MemberKey(Declared, Optional["studio.MemberKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_MemberKey | dsviper.ValueOptional | studio.MemberKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_MemberKey()

class Optional_of_Studio_PrincipalKey(Declared, Optional["studio.PrincipalKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_PrincipalKey | dsviper.ValueOptional | studio.PrincipalKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_PrincipalKey()

class Optional_of_Studio_Profile(Declared, Optional["studio.Profile"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Studio_Profile | dsviper.ValueOptional | studio.Profile | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Studio_Profile()

class Optional_of_Tuto_Account(Declared, Optional["tuto.Account"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_Account | dsviper.ValueOptional | tuto.Account | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_Account()

class Optional_of_Tuto_Identity(Declared, Optional["tuto.Identity"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_Identity | dsviper.ValueOptional | tuto.Identity | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_Identity()

class Optional_of_Tuto_Login(Declared, Optional["tuto.Login"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_Login | dsviper.ValueOptional | tuto.Login | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_Login()

class Optional_of_Tuto_Texture(Declared, Optional["tuto.Texture"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_Texture | dsviper.ValueOptional | tuto.Texture | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_Texture()

class Optional_of_Tuto_Thumbnail(Declared, Optional["tuto.Thumbnail"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_Thumbnail | dsviper.ValueOptional | tuto.Thumbnail | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_Thumbnail()

class Optional_of_Tuto_UserKey(Declared, Optional["tuto.UserKey"]):
    __slots__ = ()

    def __init__(self, value: Optional_of_Tuto_UserKey | dsviper.ValueOptional | tuto.UserKey | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_optional_Tuto_UserKey()
class Vector_of_string(Declared, Vector["str"]):
    __slots__ = ()

    def __init__(self, value: Vector_of_string | dsviper.ValueVector | typing.Sequence[str] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_vector_string()
class Set_of_string(Declared, SetView["str"]):
    __slots__ = ()

    def __init__(self, value: Set_of_string | dsviper.ValueSet | typing.Iterable[str] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_set_string()

class Set_of_Studio_MemberKey(Declared, SetView["studio.MemberKey"]):
    __slots__ = ()

    def __init__(self, value: Set_of_Studio_MemberKey | dsviper.ValueSet | typing.Iterable[studio.MemberKey] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_set_Studio_MemberKey()

class Set_of_Studio_PrincipalKey(Declared, SetView["studio.PrincipalKey"]):
    __slots__ = ()

    def __init__(self, value: Set_of_Studio_PrincipalKey | dsviper.ValueSet | typing.Iterable[studio.PrincipalKey] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_set_Studio_PrincipalKey()

class Set_of_Tuto_UserKey(Declared, SetView["tuto.UserKey"]):
    __slots__ = ()

    def __init__(self, value: Set_of_Tuto_UserKey | dsviper.ValueSet | typing.Iterable[tuto.UserKey] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_set_Tuto_UserKey()
class Map_of_string_to_string(Declared, Mapping["str", "str"]):
    __slots__ = ()

    def __init__(self, value: Map_of_string_to_string | dsviper.ValueMap | dict[str, str] | None = None) -> None:
        super().__init__(value)

    @classmethod
    def type(cls) -> dsviper.Type:
        return _type_map_string_to_string()

from . import tuto  # noqa: E402
from . import studio  # noqa: E402

declare(Optional_of_AnyConceptKey, Optional_of_string, Optional_of_Studio_AdminKey, Optional_of_Studio_Credentials, Optional_of_Studio_DeviceKey, Optional_of_Studio_MemberKey, Optional_of_Studio_PrincipalKey, Optional_of_Studio_Profile, Optional_of_Tuto_Account, Optional_of_Tuto_Identity, Optional_of_Tuto_Login, Optional_of_Tuto_Texture, Optional_of_Tuto_Thumbnail, Optional_of_Tuto_UserKey, Vector_of_string, Set_of_string, Set_of_Studio_MemberKey, Set_of_Studio_PrincipalKey, Set_of_Tuto_UserKey, Map_of_string_to_string)
