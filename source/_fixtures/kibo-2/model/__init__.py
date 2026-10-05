# Generated from model.dsm.json by kibo-2.0.0.jar. Do not edit by hand.
# Templates: kibo-template-viper 2.0.0 (MIT), Template Model 2.
# Runtime: this file imports `dsviper` >=1.2.29 <1.3.0,
# distributed under LicenseRef-DigitalSubstrate-Commercial-1.2.
# Commercial use requires a Commercial Licence from Digital Substrate.

"""The model model, generated over dsviper.

Each DSM namespace is a module holding its structures, enumerations and keys, and its
attachments as `attachments`:
`model.tuto`, `model.studio`.
`containers` holds one class per container shape the model uses, in a structure, an
attachment or a pool; another shape is built with the runtime, from Viper values:
`dsviper.Value.create(dsviper.TypeSet(model.studio.AdminKey.type()), [k.unwrap_value() for k in keys])`.
`definitions()` is the model.

A document is stored in a dsviper database that knows the model, and read and written
through an attachment, given the database or a state:

    db = dsviper.Database.create_in_memory()     # a CommitDatabase keeps every commit
    db.extend_definitions(model.definitions())
    db.begin_transaction()
    model.studio.attachments.Member.profile.set(db, key, document)
    db.commit()

A generated object is a box around a Viper value: `p.unwrap_value()` gives it, and
`Cls.wrap_value(value)` boxes one. A runtime feature is called on that value: bytes are
`dsviper.Value.encode(p.unwrap_value())`, read back with
`Cls.wrap_value(dsviper.Value.decode(blob, Cls.type(), definitions(), encoded=False))`, which
asks for the Viper value rather than natives. wrap_value or a constructor given a Viper value of
another type raises TypeError; the rest is the runtime's to refuse, with dsviper.ViperError:
content that does not fit, native or generated, in a field, a container or an attachment.
"""

import base64 as _base64
import functools as _functools
import zlib as _zlib

import dsviper as _dsviper

from . import resources
from ._codegen import AnyConceptKey, AnyValue, AttachmentProxy, Key

__all__ = ["AnyConceptKey", "AnyValue", "AttachmentProxy", "Key", "containers", "definitions", "tuto", "studio"]

@_functools.cache
def definitions() -> _dsviper.DefinitionsConst:
    """The model's definitions, decoded once: what a database is extended with, and what
    decoding a value needs."""
    blob = _dsviper.ValueBlob(_zlib.decompress(_base64.b64decode(resources.B64_DEFINITIONS)))
    return _dsviper.Definitions.decode(blob).const()


from . import containers  # noqa: E402
from . import tuto  # noqa: E402
from . import studio  # noqa: E402
