import atom
from lxml import etree


def test_feed():
    e_link = atom.Element(name="link",
                          href="http://example.org/2003/12/13/atom03")
    entry = atom.Entry(title="Atom-Powered Robots Run Amok",
                       link=e_link,
                       id="urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a",
                       updated="2003-12-13T18:30:02Z",
                       summary="Some text.")

    e_author = atom.Element(name="author")
    e_author.set_preverse_attrs("name", "John Doe")
    e_link = atom.Element(name="link", href="http://example.org/")
    feed = atom.Feed(title="Example Feed",
                     link=e_link,
                     updated="2003-12-13T18:30:02Z",
                     author=e_author,
                     id="urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6")
    feed.append_children(entry)

    buf = str(feed)
#    assert buf == (
#        "<?xml version=\"1.0\" encoding=\"utf-8\"?>\n"
#        "  <feed xmlns=\"http://www.w3.org/2005/Atom\">\n"
#        "  <title>Example Feed</title>\n"
#        "  <link href=\"http://example.org/\"/>\n"
#        "  <updated>2003-12-13T18:30:02Z</updated>\n"
#        "  <author>\n"
#        "    <name>John Doe</name>\n"
#        "  </author>\n"
#        "  <id>urn:uuid:60a76c80-d399-11d9-b93C-0003939e0af6</id>\n"
#        "  <entry>\n"
#        "    <title>Atom-Powered Robots Run Amok</title>\n"
#        "    <link href=\"http://example.org/2003/12/13/atom03\"/>\n"
#        "    <id>urn:uuid:1225c695-cfb8-4ebb-aaaa-80da344efa6a</id>\n"
#        "    <updated>2003-12-13T18:30:02Z</updated>\n"
#        "    <summary>Some text.</summary>\n"
#        "  </entry>\n"
#        "</feed>\n"
#        )

    tree = etree.fromstring(buf)


if __name__ == "__main__":
    test_feed()