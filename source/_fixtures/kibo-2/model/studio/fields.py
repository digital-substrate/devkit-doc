# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

"""The name of every field of Studio's structures, as constants: code that handles a structure
through the dynamic API completes the name and a type checker checks it, where a string literal
is neither. Their paths are in the paths module."""

from __future__ import annotations

import typing

class Credentials:
    """The field names of Credentials."""
    login: typing.Final = "login"


class Name:
    """The field names of Name."""
    first: typing.Final = "first"
    last: typing.Final = "last"


class Profile:
    """The field names of Profile."""
    name: typing.Final = "name"
    tags: typing.Final = "tags"
    roles: typing.Final = "roles"
    settings: typing.Final = "settings"
    motto: typing.Final = "motto"
    level: typing.Final = "level"
