"""Pygments lexer for DSM (Digital Substrate Model) language."""

from pygments.lexer import RegexLexer, bygroups, words
from pygments.token import (
    Comment, Keyword, Name, Number, String, Text, Punctuation, Operator
)


class DSMLexer(RegexLexer):
    """Pygments lexer for DSM data modeling language."""

    name = 'DSM'
    aliases = ['dsm']
    filenames = ['*.dsm']

    # Keywords
    keywords = (
        'namespace', 'concept', 'any_concept', 'club', 'membership',
        'enum', 'struct', 'attachment', 'function_pool', 'attachment_function_pool',
        'mutable',
    )

    # Primitive types
    primitive_types = (
        'void', 'bool',
        'uint8', 'uint16', 'uint32', 'uint64',
        'int8', 'int16', 'int32', 'int64',
        'float', 'double',
        'blob_id', 'commit_id', 'uuid', 'string', 'blob',
    )

    # Generic/container types
    generic_types = (
        'vec', 'mat', 'tuple', 'optional', 'vector', 'set', 'map',
        'xarray', 'any', 'variant', 'key',
    )

    tokens = {
        'root': [
            # Comments (// and # styles)
            (r'//.*$', Comment.Single),
            (r'#.*$', Comment.Single),
            (r'"""', String.Doc, 'docstring'),

            # UUID in braces {xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}
            (r'\{[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}\}',
             Number.Hex),

            # "is a" as two-word keyword
            (r'\bis\s+a\b', Keyword),

            # Keywords
            (words(keywords, prefix=r'\b', suffix=r'\b'), Keyword),

            # Primitive types
            (words(primitive_types, prefix=r'\b', suffix=r'\b'), Keyword.Type),

            # Generic types (before class names to catch key, vector, etc.)
            (words(generic_types, prefix=r'\b', suffix=r'\b'), Keyword.Type),

            # key<ConceptName> pattern
            (r'(key)(<)([a-zA-Z_][a-zA-Z0-9_:]*)(>)',
             bygroups(Keyword.Type, Punctuation, Name.Class, Punctuation)),

            # Boolean literals
            (r'\b(true|false)\b', Keyword.Constant),

            # Numbers (integers and floats)
            (r'-?\d+\.\d*', Number.Float),
            (r'-?\d+', Number.Integer),

            # Strings (double and single quotes)
            (r'"', String, 'string'),
            (r"'", String, 'string_single'),

            # Enum values .EnumValue
            (r'\.[A-Za-z][a-zA-Z0-9_]*', Name.Constant),

            # Class/type names (PascalCase)
            (r'\b[A-Z][a-zA-Z0-9_]*\b', Name.Class),

            # Identifiers
            (r'\b[a-z_][a-zA-Z0-9_]*\b', Name),

            # Operators and punctuation
            (r'\.\.\.', Punctuation),  # Ellipsis for omitted code
            (r'[<>{}()\[\];,:=^²→]', Punctuation),

            # Whitespace
            (r'\s+', Text),
        ],
        'string': [
            (r'\\[\\"]', String.Escape),
            (r'"', String, '#pop'),
            (r'[^"\\]+', String),
        ],
        'string_single': [
            (r"\\[\\']", String.Escape),
            (r"'", String, '#pop'),
            (r"[^'\\]+", String),
        ],
        'docstring': [
            (r'"""', String.Doc, '#pop'),
            (r'[^"]+', String.Doc),
            (r'"(?!"")', String.Doc),
        ],
    }


def setup(app):
    """Sphinx extension setup."""
    from sphinx.highlighting import lexers
    lexers['dsm'] = DSMLexer()
    return {'version': '1.0', 'parallel_read_safe': True}
