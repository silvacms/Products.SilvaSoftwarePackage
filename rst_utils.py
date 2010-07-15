# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

from cStringIO import StringIO

from collections import namedtuple
from docutils.core import publish_parts


def line_is_rst_title_marking(line):
    """This function test if a line is only composed of the same character.
    """
    if line and line[0].isspace():
        return False
    if not line:
        return False
    first_char = line[0]
    for char in line:
        if char != first_char:
            return False
    return True


RSTFormat = namedtuple('RSTFormat', 'format double')


class RSTSection(object):
    """The RST title hierarchy is represented as a tree.
    """
    sub = None
    next = None
    previous = None
    parent = None
    lines = []

    def __init__(self, title=None, rst_format=None, lineno=0):
        self.title = title
        self.rst_format = rst_format
        self.start_lineno = lineno

    def _set_sub(self, title):
        self.sub = title
        title.parent = self

    def _set_next(self, title):
        self.next = title
        title.previous = self
        title.parent = self.parent

    def add(self, title):
        if self.rst_format is None and self.parent is None:
            # Uninitialized top node, we just use title as new top node
            return title
        if title.rst_format != self.rst_format:
            # Well, maybe we went some level up
            current = self
            while current is not None:
                if title.rst_format == current.rst_format:
                    # Yes, we want up!
                    return current.add(title)
                current = current.parent
            # Well, maybe we are going one level down then
            self._set_sub(title)
            return self.sub
        # This title is at the same level than the current one
        self._set_next(title)
        return self.next

    def linenos(self):
        end = None
        if self.next is not None:
            end = self.next.start_lineno
        return (self.start_lineno, end)

    def search(self, criteria):
        """Search for a node.
        """
        matches = []
        if criteria(self):
            matches.append(self)
        for node in [self.sub, self.next]:
            if node is not None:
                matches.extend(node.search(criteria))
        return matches

    def get_root(self):
        if self.parent is None and self.rst_format is None:
            return None
        current = self
        while current.parent is not None:
            current = current.parent
        while current.previous is not None:
            current = current.previous
        return current

    def write(self, stream, following_ones=True):
        """Write the current section to the given stream.
        """
        header = ['']
        if self.rst_format.double:
            header.append(self.rst_format.format * len(self.title))
        header.append(self.title)
        header.append(self.rst_format.format * len(self.title))
        header.append('')
        stream.write('\n'.join(header))
        stream.write('\n'.join(self.lines))
        if self.sub is not None:
            self.sub.write(stream, following_ones=True)
        if following_ones and self.next is not None:
            self.next.write(stream, following_ones=True)

    def as_html(self, following_ones=False):
        rst = StringIO()
        self.write(rst, following_ones=following_ones)
        return publish_parts(
            rst.getvalue(),
            parser_name='restructuredtext',
            writer_name='html')['whole']

    def copy(self, exclude=None):
        """Copy the structure, excluding some nodes if wanted.
        """
        if exclude is None:
            exclude = lambda n: False

        def  linked_copy(node, parent=None, previous=None):
            if exclude(node):
                # Node excluded, 'we' jump it.
                if node.next is not None:
                    return linked_copy(node.next, parent, previous)
                return None

            copy = RSTSection(node.title, node.rst_format, node.start_lineno)
            copy.parent = parent
            copy.previous = previous
            copy.lines = node.lines
            if node.sub is not None:
                copy.sub = linked_copy(node.sub, copy, None)
            if node.next is not None:
                copy.next = linked_copy(node.next, parent, copy)

            return copy

        return linked_copy(self, self.parent, self.previous)

    def __str__(self):
        start_lineno, end_lineno = self.linenos()
        string = u"%s (lines %04s-%04s)" % (
            self.title, start_lineno, end_lineno)
        if self.sub:
            string += '\n' + ''.join(
                map(lambda s: '  %s\n' % s,
                    str(self.sub).split('\n'))).rstrip()
        if self.next:
            string += '\n' + str(self.next)
        return string


def rst_parser(lines):
    """Extract rst structure.
    """
    current_title = RSTSection()
    previous_line = None
    previous_line_is_empty = True
    double_title_marking = False
    current_lines = []

    for lineno, line in enumerate(lines):
        line = line.rstrip()

        if line_is_rst_title_marking(line):
            if current_lines:
                current_title.lines = current_lines[
                    :-(1 + int(double_title_marking))]
            if previous_line_is_empty:
                # This is a markup on two lines
                double_title_marking = True
            else:
                assert len(previous_line) == len(line), \
                    "Invalid title: %s" % (previous_line)
                current_title = current_title.add(
                    RSTSection(
                        previous_line,
                        RSTFormat(line[0], double_title_marking),
                        lineno - (1 + int(double_title_marking))))
                double_title_marking = False
                del current_lines[:]
        else:
            current_lines.append(line)
        previous_line_is_empty = not line.strip()
        previous_line = line

    return current_title.get_root()


HEADERS_CHANGES = ['changes', 'changelog', 'history']


def is_changes_header(node):
    return node.title.lower() in HEADERS_CHANGES


def get_last_changes(package_info):
    """Return the last changes from the description.
    """
    changes = package_info.search(is_changes_header)
    if len(changes) == 1:
        return changes[0].sub
    return None


def get_description(package_info):
    """Return the description without the changes.
    """
    return package_info.copy(exclude=is_changes_header)


if __name__ == '__main__':
    import sys
    input_filename = sys.argv[1]
    with open(input_filename, 'r') as input_rst:
        print "\nTitle structure\n"
        title = rst_parser(input_rst.readlines())
        print str(title)

    # Print last changes
    print "\nLast Changes\n"
    get_last_changes(title).write(sys.stdout, following_ones=False)

    print "\nDescription\n"
    get_description(title).write(sys.stdout, following_ones=True)

