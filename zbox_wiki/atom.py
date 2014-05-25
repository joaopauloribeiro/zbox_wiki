"""
TODO: separate this file into a individual module
"""
import logging
import time


logging.getLogger("atom").setLevel(logging.DEBUG)

wrap = lambda name, text : "<%s>%s</%s>" % (name, text, name)


def generate_updated(ts=None):
    """
    http://tools.ietf.org/html/rfc4287#section-3.3
    http://www.w3.org/TR/1998/NOTE-datetime-19980827
    """
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime(ts))


class NotConfirmToRFC(Exception):
    def __init__(self, msg, *args, **kwargs):
        self.msg = msg
        super(NotConfirmToRFC, self, *args, **kwargs)


class Element(object):

    def __init__(self, name, text = "", **kwargs):
        self._name = name
        self._text = text
        self._attributes = kwargs
        self._children = []

    def __str__(self):
        chunks = []
        for k, v in self._attributes.iteritems():
            chunk = "%s=\"%s\"" % (k, v)
            chunks.append(chunk)
        attrs_in_str = " ".join(chunks)

        if attrs_in_str.strip():
            attrs_in_str = " " + attrs_in_str

        if not self._text:
            chunks = []
            for child in self._children:
                if isinstance(child, (tuple, list)):
                    chunk_list = ["  %s" % str(i) for i in child]
                    chunks.extends(chunk_list)
                else:
                    chunk = "  %s" % str(child)
                    chunks.append(chunk)
            text = "\n".join(chunks)

            if text.strip():
                text = "\n" + text
        else:
            text = self._text

        if text:
            buf = "<%s%s>%s</%s>\n" % (self._name, attrs_in_str, text, self._name)
        else:
            buf = "<%s%s/>\n" % (self._name, attrs_in_str)
        return buf

    @property
    def name(self):
        return self._name

    @property
    def text(self):
        return self._text

    @property
    def children(self):
        return (v
            for k, v in self.__dict__.iteritems()
            if isinstance(v, Element))

    def append_children(self, child):
        self._children.append(child)

    def set_preverse_attrs(self, k, v):
        """ walk around for
         `e_author = atom.Element(name="author", name="John Doe")`

         `e_author = atom.Element(name="author")`
         `e_author.set_preverse_attrs("name", "John Doe")`
         ->
         <author>
           <name>Join Doe</name>
        </author>
        """
        assert k in ("name", "text")
        self._attributes[k] = v


class AtomElement(Element):

    def _init(self, **kwargs):
        for k, v in kwargs.iteritems():
            if k not in self.__dict__:
                msg = "un-expected key `%s`" % k
                logging.error(msg)
                raise KeyError

            if isinstance(v, Element):
                self.__dict__[k] = v
            elif isinstance(v, basestring):
                self.__dict__[k] = Element(name=k, text=v)
            else:
                msg = "expected `%s`'s value in (Element, basestring), got `%s`" % (k, str(v))
                logging.error(msg)
                raise TypeError


class Entry(AtomElement):

    def __init__(self, **kwargs):
        super(Entry, self).__init__(name="entry")

        self.author = None
        self.category = None
        self.content = None
        self.contributor = None
        self.id = None

        self.link = None
        self.published = None
        self.rights = None
        self.source = None
        self.summary = None

        self.title = None
        self.updated = None
        self.extensionElement = None

        self._multiple_elements = ("category", "contributor")
        self._single_elements = ("published", "rights", "source", "summary", "title", "updated")

        self._required = ("id", "title", "updated")

        self._init(**kwargs)

    def __str__(self):
        for k in self._required:
            if not self.__dict__[k]:
                msg = "expected Entry:%s is not None, got None" % k
                logging.error(msg)
                raise NotConfirmToRFC(msg)

        if (not self.content) and (not self.link):
            msg = "expected Entry:content or entry:link is not None, got both None"
            raise NotConfirmToRFC(msg)

        old_children = self._children[:]
        self._children.extend(self.children)
        buf = super(Entry, self).__str__()
        self._children = old_children

        return buf


class Feed(AtomElement):
    TEMPLATE = (
        "<?xml version=\"1.0\" encoding=\"utf-8\" ?>\n"
        "%s"
        )

    def __init__(self, **kwargs):
        super(Feed, self).__init__(name="feed", xmlns="http://www.w3.org/2005/Atom")

        self.author = None
        self.category = None
        self.contributor = None
        self.generator = None
        self.icon = None

        self.id = None
        self.link = None
        self.logo = None
        self.rights = None
        self.subtitle = None

        self.title = None
        self.updated = None
        self.extensionElement = None

        self._multiple_elements = ("category", "contributor")
        self._single_elements = ("generator", "icon", "logo", "rights", "subtitle")

        self._required = ("id", "title", "updated")

        self._init(**kwargs)

    def __str__(self):
        for k in self._required:
            if not self.__dict__[k]:
                msg = "expected Feed:%s is not None, got None" % k
                logging.error(msg)
                raise NotConfirmToRFC(msg)

        if not self.author:
            for obj in self._children:
                if (not obj.author) and (not obj.source):
                    msg = "expected Atom:author is not None, or Entry:author and Entry:source is not None, got both None"
                    raise NotConfirmToRFC(msg)

        old_children = self._children[:]
        self._children.extend(self.children)
        buf = super(Feed, self).__str__()
        self._children = old_children
        buf = Feed.TEMPLATE % buf

        return buf
