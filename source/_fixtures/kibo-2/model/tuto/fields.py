# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

"""The name of every field of Tuto's structures, as constants: code that handles a structure
through the dynamic API completes the name and a type checker checks it, where a string literal
is neither. Their paths are in the paths module."""

from __future__ import annotations

import typing

class Account:
    """The field names of Account."""
    state: typing.Final = "state"


class Identity:
    """The field names of Identity."""
    firstname: typing.Final = "firstname"
    lastname: typing.Final = "lastname"


class Login:
    """The field names of Login."""
    nickname: typing.Final = "nickname"
    password: typing.Final = "password"


class Texture:
    """The field names of Texture."""
    width: typing.Final = "width"
    height: typing.Final = "height"
    pixels: typing.Final = "pixels"


class Thumbnail:
    """The field names of Thumbnail."""
    width: typing.Final = "width"
    height: typing.Final = "height"
    data: typing.Final = "data"
