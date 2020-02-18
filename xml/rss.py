import typing
from xml.etree import ElementTree as ET

from .element import Element


class RSS(Element):
    """An RSS config in a SALT proposal."""

    """XPaths for common nodes."""
    NAME = './{/PIPT/RSS/Phase2}Name'
    EXPOSURE_TIME = './{/PIPT/RSS/Phase2}RssDetector/{/PIPT/RSS/Phase2}ExposureTime/{/PIPT/Shared}Value'

    @property
    def name(self) -> str:
        """Returns the name of this RSS config.

        Returns:
            Name of this RSS config.
        """
        xpath = RSS.NAME.format(**self.namespaces)
        return self.root.find(xpath).text

    @name.setter
    def name(self, v: str):
        """Sets new name for this RSS config.

        Args:
            v: New name.
        """
        xpath = RSS.NAME.format(**self.namespaces)
        self.root.find(xpath).text = v

    @property
    def exposure_time(self) -> float:
        """Returns exposure time for this RSS config.

        Returns:
            Exposure time for this config.
        """
        return float(self.get(RSS.EXPOSURE_TIME))

    @exposure_time.setter
    def exposure_time(self, v: float):
        """Sets new exposure time for this RSS config.

        Args:
            v: New exposure time.
        """
        self.set(RSS.EXPOSURE_TIME, v)
