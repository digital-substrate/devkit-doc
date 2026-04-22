"""
Sphinx extension to inject type hints from .pyi stub files into autodoc signatures.

This extension solves the problem that Sphinx autodoc cannot extract type hints
from C extension modules. It parses the .pyi stub file and replaces signatures
in the generated documentation.

Usage:
    Add 'pyi_signatures' to extensions in conf.py
"""
import ast
import logging
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)

# Cache of parsed signatures: {qualified_name: (signature_str, return_annotation_str)}
_pyi_signatures: Dict[str, Tuple[str, Optional[str]]] = {}

# Cache of class inheritance: {class_name: [parent_class_names]}
_class_bases: Dict[str, list] = {}


def _format_annotation(node: ast.expr) -> str:
    """Convert an AST annotation node to a string representation."""
    if node is None:
        return ''
    return ast.unparse(node)


def _format_arg(arg: ast.arg) -> str:
    """Format a function argument with its annotation."""
    if arg.annotation:
        return f"{arg.arg}: {_format_annotation(arg.annotation)}"
    return arg.arg


def _format_signature(func: ast.FunctionDef) -> Tuple[str, Optional[str]]:
    """Extract signature and return annotation from a FunctionDef node."""
    args = func.args
    parts = []

    # Positional-only args (before /)
    posonlyargs = getattr(args, 'posonlyargs', [])
    for arg in posonlyargs:
        parts.append(_format_arg(arg))
    if posonlyargs:
        parts.append('/')

    # Regular positional args
    num_defaults = len(args.defaults)
    num_args = len(args.args)

    for i, arg in enumerate(args.args):
        # Skip 'self' for instance methods
        if i == 0 and arg.arg == 'self':
            continue
        # Skip 'cls' for class methods
        if i == 0 and arg.arg == 'cls':
            continue

        formatted = _format_arg(arg)

        # Add default value if present
        default_idx = i - (num_args - num_defaults)
        if default_idx >= 0 and default_idx < len(args.defaults):
            default = args.defaults[default_idx]
            formatted += f" = {ast.unparse(default)}"

        parts.append(formatted)

    # *args
    if args.vararg:
        parts.append(f"*{_format_arg(args.vararg)}")
    elif args.kwonlyargs:
        parts.append('*')

    # Keyword-only args
    for i, arg in enumerate(args.kwonlyargs):
        formatted = _format_arg(arg)
        if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
            formatted += f" = {ast.unparse(args.kw_defaults[i])}"
        parts.append(formatted)

    # **kwargs
    if args.kwarg:
        parts.append(f"**{_format_arg(args.kwarg)}")

    signature = f"({', '.join(parts)})"

    # Return annotation
    return_annotation = None
    if func.returns:
        return_annotation = _format_annotation(func.returns)

    return signature, return_annotation


def parse_pyi_file(pyi_path: Path, module_name: str) -> Tuple[Dict[str, Tuple[str, Optional[str]]], Dict[str, list]]:
    """
    Parse a .pyi file and extract all function/method signatures and class inheritance.

    Returns:
        Tuple of:
        - Dict mapping qualified names (e.g., 'dsviper.Type.encode') to
          (signature_str, return_annotation_str) tuples.
        - Dict mapping qualified class names to list of parent class names.
    """
    signatures = {}
    class_bases = {}

    try:
        source = pyi_path.read_text(encoding='utf-8')
        tree = ast.parse(source, filename=str(pyi_path))
    except (OSError, SyntaxError) as e:
        logger.warning(f"Failed to parse {pyi_path}: {e}")
        return signatures, class_bases

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            qualified_class = f"{module_name}.{class_name}"

            # Extract base classes
            bases = []
            for base in node.bases:
                if isinstance(base, ast.Name):
                    bases.append(f"{module_name}.{base.id}")
                elif isinstance(base, ast.Attribute):
                    bases.append(ast.unparse(base))
            class_bases[qualified_class] = bases

            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    method_name = item.name
                    qualified_name = f"{qualified_class}.{method_name}"

                    sig, ret = _format_signature(item)
                    signatures[qualified_name] = (sig, ret)

        elif isinstance(node, ast.FunctionDef):
            # Module-level function
            if node.col_offset == 0:  # Top-level only
                qualified_name = f"{module_name}.{node.name}"
                sig, ret = _format_signature(node)
                signatures[qualified_name] = (sig, ret)

    return signatures, class_bases


def load_pyi_signatures(app: Any) -> None:
    """Load signatures from the dsviper .pyi file at builder initialization."""
    global _pyi_signatures, _class_bases

    # Try to find the .pyi file
    try:
        import dsviper
        module_path = Path(dsviper.__file__).parent
        pyi_path = module_path / '__init__.pyi'

        if pyi_path.exists():
            _pyi_signatures, _class_bases = parse_pyi_file(pyi_path, 'dsviper')
            logger.info(f"Loaded {len(_pyi_signatures)} signatures and {len(_class_bases)} classes from {pyi_path}")
        else:
            logger.warning(f"No .pyi file found at {pyi_path}")

    except ImportError:
        logger.warning("dsviper module not found, cannot load .pyi signatures")


def _find_signature_with_inheritance(name: str) -> Optional[Tuple[str, Optional[str]]]:
    """
    Find a signature, looking up the inheritance chain if not found directly.

    For example, if looking for 'dsviper.TypeVoid.description' and it's not found,
    try 'dsviper.Type.description' (the parent class).
    """
    # Direct lookup
    if name in _pyi_signatures:
        return _pyi_signatures[name]

    # Try parent classes
    parts = name.rsplit('.', 1)
    if len(parts) == 2:
        class_name, method_name = parts
        # Check if this is a method (class_name should be like 'dsviper.TypeVoid')
        if class_name in _class_bases:
            for parent in _class_bases[class_name]:
                parent_method = f"{parent}.{method_name}"
                result = _find_signature_with_inheritance(parent_method)
                if result:
                    return result

    return None


def replace_signature(
    app: Any,
    what: str,
    name: str,
    obj: Any,
    options: Any,
    signature: Optional[str],
    return_annotation: Optional[str]
) -> Optional[Tuple[str, str]]:
    """
    Autodoc event handler to replace C extension signatures with .pyi signatures.

    This is called for each documented object. If we have a signature from the
    .pyi file, we return it to override the default. Also checks parent classes
    for inherited methods.
    """
    result = _find_signature_with_inheritance(name)
    if result:
        pyi_sig, pyi_ret = result
        return pyi_sig, pyi_ret

    return None  # Keep original signature


def setup(app: Any) -> Dict[str, Any]:
    """Sphinx extension setup."""
    app.connect('builder-inited', load_pyi_signatures)
    app.connect('autodoc-process-signature', replace_signature)

    return {
        'version': '1.0',
        'parallel_read_safe': True,
        'parallel_write_safe': True,
    }
