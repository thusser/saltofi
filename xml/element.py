import io
from xml.etree import ElementTree as ET

import typing


class Element(object):
    """Base class for all XML elements in a SALT proposal."""

    def __init__(self, source: typing.Union[str, ET.Element]):
        """Initializes a new XML element.

        Args:
            source: XML source for this element, either as filename or as ET.Element object.
        """

        # what format is proposal?
        if isinstance(source, ET.Element):
            # XML element
            self.root = source
        elif isinstance(source, str):
            # filename
            xml = ET.parse(source)
            self.root = xml.getroot()
        else:
            raise ValueError('Unknown input.')

        # get XML ns string and extract namespaces
        # this will create a dictionary self.namespaces with entries like this:
        #   '/PIPT/Proposal/Phase2': '{http://www.salt.ac.za/PIPT/Proposal/Phase2/4.8}'
        # which is used to map namespaces to the latest version
        xml = ET.tostring(self.root).decode('utf-8')
        tmp = dict([node for _, node in ET.iterparse(io.StringIO(xml), events=['start-ns'])])
        self.namespaces = {n[n.find('/PIPT'):n.rfind('/')]: '{%s}' % n for n in tmp.values()}

    def write(self, file_obj):
        """Write XML into a file-like object.

        Args:
            file_obj: File-like object.
        """
        et = ET.ElementTree(self.root)
        et.write(file_obj)

    def to_string(self):
        """Returns XML as string."""
        with io.BytesIO() as bio:
            self.write(bio)
            return bio.getvalue()

    def get_objects(self, xpath: str, klass, root=None) -> list:
        """Find all nodes described by a given xpath and create objects of the given class from it.

        Args:
            xpath: XPath for elements to search for, will be mapped using self.namespaces.
            klass: Class to use for creating objects.
            root: Alternative root for search.

        Returns:
            List of objects of type klass.
        """
        root = root if root else self.root
        return [klass(c) for c in root.findall(xpath.format(**self.namespaces))]

    def get(self, xpath: str, root=None, default=None) -> str:
        """Get the text attribute of a single node described by xpath.

        Args:
            xpath: XPath for element, will be mapped using self.namespaces.
            root: Alternative root for search.
            default: If element was not found, return this as default.

        Returns:
            Text value of given node.
        """
        root = root if root else self.root
        el = root.find(xpath.format(**self.namespaces))
        if el is None and default is not None:
            return default
        return el.text

    def set(self, xpath: str, value: str, root=None):
        """Set the text attribute of a single node described by xpath.

        Args:
            xpath: XPath for element, will be mapped using self.namespaces.
            value: New value for element's text attribute.
            root: Alternative root for search.
        """
        root = root if root else self.root
        root.find(xpath.format(**self.namespaces)).text = str(value)


__all__ = ['Element']
