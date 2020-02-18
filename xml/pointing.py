import typing
from xml.etree import ElementTree as ET

from .element import Element
from .observation import Observation


class Pointing(Element):
    """A pointing in a SALT proposal."""

    """XPaths for common nodes."""
    NAME = './{/PIPT/Proposal/Phase2}Name'
    OBSERVATION = './{/PIPT/Proposal/Phase2}Observation'

    @property
    def name(self) -> str:
        """Returns the name of this Pointing.

        Returns:
            Name of this Pointing.
        """
        return self.get(Pointing.NAME)

    @name.setter
    def name(self, v: str):
        """Sets new name for this Pointing.

        Args:
            v: New name.
        """
        self.set(Pointing.NAME, v)

    @property
    def observations(self) -> typing.List[Observation]:
        """Returns a list of all observations for this pointing.

        Returns:
            List of observations.
        """
        return self.get_objects(Pointing.OBSERVATION, Observation)


__all__ = ['Pointing']
