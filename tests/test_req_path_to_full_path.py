#!/usr/bin/env python
import os
import sys
import web

PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)
    
from zbox_wiki import default_conf as  conf


def req_path_to_full_path(req_path, pages_path = conf.pages_path):
    """
    >>> pages_path = "/tmp/pages/"
    >>> req_path_to_full_path("sandbox1", pages_path)
    '/tmp/pages/sandbox1.md'
    
    >>> req_path_to_full_path("sandbox1/", pages_path)
    '/tmp/pages/sandbox1/'
    
    >>> req_path_to_full_path("hacking/fetion/fetion-protocol/", pages_path)
    '/tmp/pages/hacking/fetion/fetion-protocol/'
    
    >>> req_path_to_full_path("hacking/fetion/fetion-protocol/method-option.md", pages_path)
    '/tmp/pages/hacking/fetion/fetion-protocol/method-option.md'
    """

    req_path = web.rstrips(req_path, ".md")
    req_path = web.rstrips(req_path, ".markdown")
    
    if not req_path.endswith("/"):
        path_md = "%s.md" % os.path.join(pages_path, req_path)
        path_markdown = "%s.markdown" % os.path.join(pages_path, req_path)
        
        if os.path.exists(path_md):
            return path_md
        elif os.path.exists(path_markdown):
            return path_markdown
        else:
            return path_md
    elif req_path == "/":
        return pages_path
    else:
        return os.path.join(pages_path, req_path)

if __name__ == "__main__":
    import doctest
    doctest.testmod()
