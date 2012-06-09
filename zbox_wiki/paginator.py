#!/usr/bin/env python
import math

__all__ = [
    "Paginator",
]


class Paginator(object):
    def __init__(self):
        self.current_offset = 0

        self.total = None
        self.limit = None
        self.url = None

    @property
    def count(self):
        """
        DON'T USE round build-in method, use math.ceil() instead.

        http://php.net/manual/en/function.round.php
        http://docs.python.org/library/math.html
        """
        return int(math.ceil(self.total * 1.0 / self.limit))

    @property
    def previous_page_url(self):
        return "%s?limit=%d&offset=%d" % (self.url, self.limit, self.current_offset - 1)

    @property
    def next_page_url(self):
        return "%s?limit=%d&offset=%d" % (self.url, self.limit, self.current_offset + 1)

    @property
    def has_previous_page(self):
        return self.current_offset > 0

    @property
    def has_next_page(self):
        return (self.current_offset * self.limit + self.limit) < self.total
