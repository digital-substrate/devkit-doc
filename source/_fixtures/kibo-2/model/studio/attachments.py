# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.2 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

from __future__ import annotations

import dsviper

from .. import definitions
import typing

from .._codegen import AnyConceptKey, AnyValue, AttachmentProxy
from .. import containers
from .. import studio

class Member:
    class _Profile(AttachmentProxy[studio.MemberKey, studio.Profile, containers.Set_of_Studio_MemberKey, studio.Profile]):

        def set_name(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: studio.Name) -> None:
            self._update(mutating, key, "name", value)

        def set_tags(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Vector_of_string | typing.Sequence[str]) -> None:
            self._update(mutating, key, "tags", value)

        def set_roles(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Set_of_string | typing.Iterable[str]) -> None:
            self._update(mutating, key, "roles", value)

        def union_roles(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Set_of_string) -> None:
            self._union_in_set(mutating, key, "roles", value)

        def subtract_roles(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Set_of_string) -> None:
            self._subtract_in_set(mutating, key, "roles", value)

        def set_settings(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Map_of_string_to_string | dict[str, str]) -> None:
            self._update(mutating, key, "settings", value)

        def union_settings(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Map_of_string_to_string) -> None:
            self._union_in_map(mutating, key, "settings", value)

        def subtract_settings(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Set_of_string) -> None:
            self._subtract_in_map(mutating, key, "settings", value)

        def update_settings(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Map_of_string_to_string) -> None:
            self._update_in_map(mutating, key, "settings", value)

        def set_motto(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: containers.Optional_of_string | str | None) -> None:
            self._update(mutating, key, "motto", value)

        def set_level(self, mutating: dsviper.AttachmentMutating, key: studio.MemberKey, value: int) -> None:
            self._update(mutating, key, "level", value)

    profile = _Profile(
        dsviper.ValueUUId.create("f95c9ae2-1f1f-1725-9408-8d7c63579401"), definitions, studio.MemberKey, studio.Profile)

class Principal:
    class _Credentials(AttachmentProxy[studio.PrincipalKey, studio.Credentials, containers.Set_of_Studio_PrincipalKey, studio.Credentials]):

        def set_login(self, mutating: dsviper.AttachmentMutating, key: studio.PrincipalKey, value: str) -> None:
            self._update(mutating, key, "login", value)

    credentials = _Credentials(
        dsviper.ValueUUId.create("06c78884-fffc-4275-5fdb-76580f1d8594"), definitions, studio.PrincipalKey, studio.Credentials)
