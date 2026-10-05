# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

from __future__ import annotations

import dsviper

from .. import definitions
import typing

from .._codegen import AnyConceptKey, AnyValue, AttachmentProxy
from .. import containers
from .. import tuto

class User:
    class _Account(AttachmentProxy[tuto.UserKey, tuto.Account, containers.Set_of_Tuto_UserKey, tuto.Account]):

        def set_state(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: tuto.Status) -> None:
            self._update(mutating, key, "state", value)

    account = _Account(
        dsviper.ValueUUId.create("ddff38a1-01b4-1979-d576-ca655a092bb8"), definitions, tuto.UserKey, tuto.Account)

    class _Avatar(AttachmentProxy[tuto.UserKey, tuto.Thumbnail, containers.Set_of_Tuto_UserKey, tuto.Thumbnail]):

        def set_width(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: int) -> None:
            self._update(mutating, key, "width", value)

        def set_height(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: int) -> None:
            self._update(mutating, key, "height", value)

        def set_data(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: dsviper.ValueBlob) -> None:
            self._update(mutating, key, "data", value)

    avatar = _Avatar(
        dsviper.ValueUUId.create("0e866bc1-5074-3f2d-ef04-ae847fb115ff"), definitions, tuto.UserKey, tuto.Thumbnail)

    class _Identity(AttachmentProxy[tuto.UserKey, tuto.Identity, containers.Set_of_Tuto_UserKey, tuto.Identity]):

        def set_firstname(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: str) -> None:
            self._update(mutating, key, "firstname", value)

        def set_lastname(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: str) -> None:
            self._update(mutating, key, "lastname", value)

    identity = _Identity(
        dsviper.ValueUUId.create("cc54d554-b8de-9960-cba3-40c04dc05b3a"), definitions, tuto.UserKey, tuto.Identity)

    class _Login(AttachmentProxy[tuto.UserKey, tuto.Login, containers.Set_of_Tuto_UserKey, tuto.Login]):

        def set_nickname(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: str) -> None:
            self._update(mutating, key, "nickname", value)

        def set_password(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: str) -> None:
            self._update(mutating, key, "password", value)

    login = _Login(
        dsviper.ValueUUId.create("438491ed-5518-5d0c-9836-920ee80dd0e8"), definitions, tuto.UserKey, tuto.Login)

    class _Portrait(AttachmentProxy[tuto.UserKey, tuto.Texture, containers.Set_of_Tuto_UserKey, tuto.Texture]):

        def set_width(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: int) -> None:
            self._update(mutating, key, "width", value)

        def set_height(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: int) -> None:
            self._update(mutating, key, "height", value)

        def set_pixels(self, mutating: dsviper.AttachmentMutating, key: tuto.UserKey, value: dsviper.ValueBlobId) -> None:
            self._update(mutating, key, "pixels", value)

    portrait = _Portrait(
        dsviper.ValueUUId.create("f24b9e5f-f39a-98c3-7cce-ea08538b6d0b"), definitions, tuto.UserKey, tuto.Texture)
