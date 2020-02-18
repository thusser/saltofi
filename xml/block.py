import typing
from xml.etree import ElementTree as ET

from .element import Element
from .pointing import Pointing
from .target import Target


class Block(Element):
    """A block in a SALT proposal."""

    """XPaths for common nodes."""
    BLOCK_CODE = './{/PIPT/Proposal/Phase2}BlockCode'
    NAME = './{/PIPT/Proposal/Phase2}Name'
    COMMENTS = './{/PIPT/Proposal/Phase2}BlockSemester/{/PIPT/Proposal/Phase2}Comments'
    YEAR = './{/PIPT/Proposal/Phase2}BlockSemester/{/PIPT/Proposal/Phase2}Year'
    SEMESTER = './{/PIPT/Proposal/Phase2}BlockSemester/{/PIPT/Proposal/Phase2}Semester'

    @property
    def name(self) -> str:
        """Returns the name of this block.

        Returns:
            Name of this block.
        """
        return self.get(Block.NAME)

    @name.setter
    def name(self, v: str):
        """Sets new name for this block.

        Args:
            v: New name.
        """
        self.set(Block.NAME, v)

    @property
    def code(self) -> str:
        """Returns the code of this block.

        Returns:
            Code of this block.
        """
        return self.get(Block.BLOCK_CODE)

    @code.setter
    def code(self, v: str):
        """Sets new code for this block.

        Args:
            v: New code.
        """
        self.set(Block.BLOCK_CODE, v)

    @property
    def comment(self) -> str:
        """Returns the comment for this block.

        Returns:
            Comment for this block.
        """
        return self.get(Block.COMMENTS)

    @comment.setter
    def comment(self, v: str):
        """Sets new comment for this block.

        Args:
            v: New comment.
        """
        self.set(Block.COMMENTS, v)

    @property
    def semester(self) -> str:
        """Returns the semester for this block.

        Returns:
            Semester for this block.
        """
        return int(self.get(Block.SEMESTER))

    @semester.setter
    def semester(self, v: int):
        """Sets new semester for this block.

        Args:
            v: New semester.
        """
        self.set(Block.SEMESTER, str(v))

    @property
    def year(self):
        """Returns the year for this block.

        Returns:
            Year for this block.
        """
        return int(self.get(Block.YEAR))

    @year.setter
    def year(self, v: int):
        """Sets new year for this block.

        Args:
            v: New year.
        """
        self.set(Block.YEAR, str(v))

    @property
    def pointings(self) -> typing.List[Pointing]:
        """Returns all Pointings within this block.

        Returns:
            List of Pointing objects.
        """
        xpath = './{/PIPT/Proposal/Phase2}SubBlock' \
                '/{/PIPT/Proposal/Phase2}SubSubBlock' \
                '/{/PIPT/Proposal/Phase2}Pointing'.format(**self.namespaces)
        return [Pointing(p) for p in self.root.findall(xpath)]

    @property
    def targets(self) -> typing.List[Target]:
        """Returns all Targets within this block.

        Returns:
            List of Target objects.
        """
        xpath = './{/PIPT/Proposal/Phase2}SubBlock' \
                '/{/PIPT/Proposal/Phase2}SubSubBlock' \
                '/{/PIPT/Proposal/Phase2}Pointing' \
                '/{/PIPT/Proposal/Phase2}Observation' \
                '/{/PIPT/Proposal/Phase2}Acquisition' \
                '/{/PIPT/Proposal/Shared}Target' .format(**self.namespaces)
        return [Target(t) for t in self.root.findall(xpath)]


__all__ = ['Block']
