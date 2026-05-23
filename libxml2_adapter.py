"""
This module provides a compatibility layer between libxml2 and lxml.
It implements the libxml2 API using lxml, allowing code that was written for libxml2
to work with lxml instead.
"""

import lxml.etree as ET
from lxml import etree

def parseFile(filename):
    """Parse an XML file and return a document object."""
    return Document(etree.parse(filename))

class Document:
    def __init__(self, etree_doc):
        self.doc = etree_doc
        
    def xpathNewContext(self):
        """Create a new XPath context for this document."""
        return XPathContext(self.doc)
        
    def saveFile(self, filename):
        """Save the document to a file."""
        self.doc.write(filename, encoding='utf-8', xml_declaration=True, pretty_print=True)
        
    def xpathEval(self, xpath_expr):
         results = self.doc.getroot().xpath(xpath_expr)
         return [Node(r) if hasattr(r, 'tag') else r for r in results]

class XPathContext:
    def __init__(self, doc):
        self.doc = doc
        self.nsmap = {}

    def xpathEval(self, xpath_expr):
        results = self.doc.getroot().xpath(xpath_expr)
        return [Node(r) if hasattr(r, 'tag') else r for r in results]
        

class Node:
    def __init__(self, etree_node):
        self.node = etree_node
        self.content = self._get_content()
        
    def _get_content(self):
        """Get the text content of this node."""
        if hasattr(self.node, 'text') and self.node.text is not None:
            return self.node.text
        return ""

    def xpathEval(self, xpath_expr):
        results = self.node.xpath(xpath_expr)
        return [Node(r) if hasattr(r, 'tag') else r for r in results]

            
    def addChild(self, node):
        """Add a child node to this node."""
        if isinstance(node, Node):
            self.node.append(node.node)
        else:
            # Assume it's a new node name
            child = etree.SubElement(self.node, node)
            return Node(child)
            
    def addSibling(self, node):
        """Add a sibling node after this node."""
        if isinstance(node, Node):
            self.node.addnext(node.node)
        else:
            # Assume it's a new node name
            sibling = etree.Element(node)
            self.node.addnext(sibling)
            return Node(sibling)
            
    def setContent(self, content):
        """Set the text content of this node."""
        self.node.text = content
        self.content = content

def newNode(name):
    """Create a new XML node with the given name."""
    return Node(etree.Element(name))


