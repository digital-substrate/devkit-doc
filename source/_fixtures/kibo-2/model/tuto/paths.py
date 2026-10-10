# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

"""The path of every field of Tuto's structures, for code that reads or writes a field
through the dynamic API. The field names are in the fields module."""

from __future__ import annotations

import typing

import dsviper

from . import fields

class Account:
    """The field paths of Account."""
    state: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Account.state).const()


class Identity:
    """The field paths of Identity."""
    firstname: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Identity.firstname).const()
    lastname: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Identity.lastname).const()


class Login:
    """The field paths of Login."""
    nickname: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Login.nickname).const()
    password: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Login.password).const()


class Texture:
    """The field paths of Texture."""
    width: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Texture.width).const()
    height: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Texture.height).const()
    pixels: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Texture.pixels).const()


class Thumbnail:
    """The field paths of Thumbnail."""
    width: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Thumbnail.width).const()
    height: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Thumbnail.height).const()
    data: typing.Final[dsviper.PathConst] = dsviper.Path.from_field(fields.Thumbnail.data).const()
