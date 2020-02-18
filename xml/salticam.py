import typing
from xml.etree import ElementTree as ET

from .element import Element


class Salticam(Element):
    """A Salticam config in a SALT proposal."""

    """XPaths for common nodes."""
    NAME = './{/PIPT/Salticam/Phase2}Name'

    @property
    def name(self) -> str:
        """Returns the name of this Salticam config.

        Returns:
            Name of this Salticam config.
        """
        xpath = Salticam.NAME.format(**self.namespaces)
        return self.root.find(xpath).text

    @name.setter
    def name(self, v: str):
        """Sets new name for this Salticam config.

        Args:
            v: New name.
        """
        xpath = Salticam.NAME.format(**self.namespaces)
        self.root.find(xpath).text = v


__all__ = ['Salticam']
