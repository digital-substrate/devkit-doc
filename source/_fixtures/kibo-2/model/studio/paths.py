# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

"""The path of every field of Studio's structures, for code that reads or writes a field
through the dynamic API. The field names are in the fields module."""

from __future__ import annotations

import typing

import dsviper

from . import fields

class Credentials:
    """The field paths of Credentials."""
    login: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Credentials.login).const()


class Name:
    """The field paths of Name."""
    first: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Name.first).const()
    last: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Name.last).const()


class Profile:
    """The field paths of Profile."""
    name: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.name).const()
    tags: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.tags).const()
    roles: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.roles).const()
    settings: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.settings).const()
    motto: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.motto).const()
    level: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Profile.level).const()
