import typing
from xml.etree import ElementTree as ET

from .element import Element
from .target import Target


class Observation(Element):
    """An observation in a SALT proposal."""

    """XPaths for common nodes."""
    PAYLOAD_CONFIG = './{/PIPT/Proposal/Phase2}TelescopeConfig/{/PIPT/Proposal/Phase2}PayloadConfig'
    RSS = PAYLOAD_CONFIG + '/{/PIPT/RSS/Phase2}Rss'
    SALTICAM = PAYLOAD_CONFIG + '/{/PIPT/Salticam/Phase2}Salticam'
    TARGET = './{/PIPT/Proposal/Phase2}Acquisition/{/PIPT/Proposal/Shared}Target'
    NAME = './{/PIPT/Proposal/Phase2}Name'

    @property
    def name(self) -> str:
        """Returns the name of this observation.

        Returns:
            Name of this observation.
        """
        return self.get(Observation.NAME)

    @name.setter
    def name(self, v: str):
        """Sets new name for this observation.

        Args:
            v: New name.
        """
        self.set(Observation.NAME, v)

    @property
    def instrument_configs(self) -> list:
        """Return a list of all RSS and Salticam configurations in this observation.

        Returns:
            List of RSS/Salticam configs.
        """
        from .rss import RSS
        from .salticam import Salticam

        # get configs
        rss = self.get_objects(Observation.RSS, RSS)
        salticam = self.get_objects(Observation.SALTICAM, Salticam)
        return rss + salticam

    @property
    def targets(self) -> typing.List[Target]:
        """Returns list of targets in this observation.

        Returns:
            List of targets.
        """
        return self.get_objects(Observation.TARGET, Target)


__all__ = ['Observation']

