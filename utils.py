# Copyright (c) 2004-2010 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$


def line_is_rst_title_marking(line):
    """This function test if a line is only composed of the same character.
    """
    if line and line[0].isspace():
        return False
    line = line.strip()
    if not line:
        return False
    first_char = line[0]
    for char in line:
        if char != first_char:
            return False
    return True


class RSTTitle(object):
    """The RST title hierarchy is represented as a tree.
    """

    subtitle = None
    nexttitle = None
    previoustitle = None
    parent = None

    def __init__(self, title=None, rst_format=None):
        self.title = title
        self.rst_format = rst_format

    def _set_subtitle(self, title):
        self.subtitle = title
        title.parent = self

    def _set_nexttitle(self, title):
        self.nexttitle = title
        title.previoustitle = title
        title.parent = self.parent

    def add(self, title):
        if self.rst_format is None and self.parent is None:
            # Uninitialized top node, we just use title as new top node
            return title
        if title.rst_format != self.rst_format:
            # Well, maybe we went some level up
            current = self
            while current.parent:
                if title.rst_format == current.rst_format:
                    # Yes, we want up!
                    current.add(title)
                    return current
            # Well, maybe we are going one level down then
            self._set_subtitle(title)
            return self.subtitle
        # This title is at the same level than the current one
        self._set_nexttitle(title)
        return self.nexttitle

    def main_title(self):
        if self.parent is None and self.rst_format is None:
            return None
        current = self
        while current.parent:
            current = current.parent
        while current.previoustitle:
            current = current.previoustitle
        return current

    def __str__(self):
        return u"%s" % self.title


def rst_titles_parser(lines):
    """Extract rst title structure.
    """
    current_title = RSTTitle()
    previous_line = None
    previous_line_is_title_marking = False

    for line_number, line in enumerate(lines):
        if previous_line is None or previous_line_is_title_marking:
            previous_line_is_title_marking = False
            previous_line = line
            continue

        if line_is_rst_title_marking(line):
            current_title = current_title.add(RSTTitle(previous_line, line[0]))
            previous_line_is_title_marking = True

        previous_line = line

    return current_title.main_title()
