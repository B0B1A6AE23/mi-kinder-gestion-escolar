"""Utilidades para la app web."""
import unicodedata


def unaccent(s):
    """Elimina acentos de un string para busqueda insensible."""
    if s is None:
        return None
    return "".join(
        c for c in unicodedata.normalize("NFD", s)
        if unicodedata.category(c) != "Mn"
    ).lower()
