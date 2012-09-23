#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os
import re
import logging

import consts
import commons
import shell
import web


logging.getLogger("mdutils").setLevel(logging.DEBUG)

try:
    import graphviz2png
except ImportError:
    graphviz2png = None
    logging.warn("import graphviz2png module failed")

try:
    import tex2png
except ImportError:
    tex2png = None
    logging.warn("import tex2png module failed")

import md_table
import markdown
import macro_cat


__all__ = [
    "text_path_to_button_path",
    "md2html",
    "zw_macro2md",
    "sequence_to_unorder_list",
]


def trac_wiki_code_block_to_md_code(text):
    """ This API deprecated in the future. """
    alias_p = '[a-zA-Z0-9#\-\+ \.]'
    shebang_p = '(?P<shebang_line>[\s]*#!%s{1,21}[\s]*?)' % alias_p

    code_p = '(?P<code>[^\f\v]+?)'

    code_block_p = "^\{\{\{[\s]*%s*%s[\s]*\}\}\}" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        buf = "\n    ".join(code.split(os.linesep))
        buf = "    %s" % buf
        return buf

    return p_obj.sub(code_repl, text)

def code_block_to_md_code(text):
    alias_p = '[a-zA-Z0-9#\-\+ \.]'
    shebang_p = '(?P<shebang_line>[\s]*#!%s{1,21}[\s]*?)' % alias_p

    code_p = '(?P<code>[^\f\v]+?)'

    code_block_p = "^```[\s]*%s*%s[\s]*```" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        buf = "\n    ".join(code.split(os.linesep))
        buf = "    %s" % buf
        return buf

    return p_obj.sub(code_repl, text)

def macro_tex2md(text, save_to_prefix, **macro_graphviz2md):
    shebang_p = "#!tex"
    code_p = '(?P<code>[^\f\v]+?)'
    code_block_p = "^\{\{\{[\s]*%s*%s[\s]*\}\}\}" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        png_filename = tex2png.tex_text2png(text = code, save_to_prefix = save_to_prefix)

        return "![%s](%s)" % (png_filename, png_filename)

    return p_obj.sub(code_repl, text)

def macro_graphviz2md(text, save_to_prefix, **view_settings):
    shebang_p = "#!graphviz"
    code_p = '(?P<code>[^\f\v]+?)'
    code_block_p = "^\{\{\{[\s]*%s*%s[\s]*\}\}\}" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        dst_path = graphviz2png.dot_text2png(text = code, png_path = save_to_prefix)
        png_filename = os.path.basename(dst_path)

        return "![%s](%s)" % (png_filename, png_filename)

    return p_obj.sub(code_repl, text)


def _fix_img_url(text, static_file_prefix = None):
    """
        >>> text = '![blah blah](20100426-400x339.png)'
        >>> static_file_prefix = '/static/files/'
        >>> _fix_img_url(text, static_file_prefix)
        '![blah blah](/static/files/20100426-400x339.png)'
    """
    def img_url_repl(match_obj):
        img_alt = match_obj.group("img_alt")
        img_url = match_obj.group("img_url")
        if static_file_prefix:
            fixed_img_url = os.path.join(static_file_prefix, img_url)
            return '![%s](%s)' % (img_alt, fixed_img_url)
        else:
            return '![%s](%s)' % (img_alt, img_url)

    img_url_p = r"!\[(?P<img_alt>.+?)\]\((?P<img_url>[^\s]+?)\)"
    img_url_p_obj = re.compile(img_url_p, re.MULTILINE)
    return img_url_p_obj.sub(img_url_repl, text)

def _fix_img_url_with_option(text, static_file_prefix = None):
    """
        >>> text = '![blah blah](20100426-400x339.png "png title")'
        >>> static_file_prefix = '/static/files/'
        >>> _fix_img_url_with_option(text, static_file_prefix)
        '![blah blah](/static/files/20100426-400x339.png "png title")'
    """
    def img_url_repl(match_obj):
        img_alt = match_obj.group('img_alt')
        img_url = match_obj.group('img_url')
        img_title = match_obj.group('img_title')
        if static_file_prefix:
            fixed_img_url = os.path.join(static_file_prefix, img_url)
            return '![%s](%s "%s")' % (img_alt, fixed_img_url, img_title)
        else:
            return '![%s](%s "%s")' % (img_alt, img_url, img_title)

    img_url_p = r"!\[(?P<img_alt>.+?)\]\((?P<img_url>[^\s]+?)\s\"(?P<img_title>.+?)\"\)"
    img_url_p_obj = re.compile(img_url_p, re.MULTILINE)
    return img_url_p_obj.sub(img_url_repl, text)

def uri2html_link(text):
    """ References:

     - http://stackoverflow.com/questions/6718633/python-regular-expression-again-match-url
     - http://daringfireball.net/2010/07/improved_regex_for_matching_urls
    """
    p = r'''(?i)\b((?:[a-z][\w-]+:(?:/{1,3}|[a-z0-9%])|www\d{0,3}[.]|[a-z0-9.\-]+[.][a-z]{2,4}/)(?:[^\s()<>]+|\(([^\s()<>]+|(\([^\s()<>]+\)))*\))+(?:\(([^\s()<>]+|(\([^\s()<>]+\)))*\)|[^\s`!()\[\]{};:'".,<>?«»“”‘’]))'''
    p_obj = re.compile(p, re.UNICODE | re.MULTILINE)

    def repl(match_obj):
        url = match_obj.groups()[0]
        return '<a href="%s">%s</a>' % (url, url)

    return p_obj.sub(repl, text)

def convert_static_file_url(text, static_file_prefix):
    text = _fix_img_url(text, static_file_prefix)
    text = _fix_img_url_with_option(text, static_file_prefix)
    return text


def path2hierarchy(path):
    """ Parse path and return hierarchy name and link pairs,
    inspired by [GNOME Nautilus](http://library.gnome.org/users/user-guide/2.32/nautilus-location-bar.html.en)
    and [Trac Wiki](http://trac.edgewall.org/browser/trunk/trac/wiki/web_ui.py) .

        >>> path = '/shugelab/users/lee'
        >>> t1 = [('shugelab', '/shugelab'), ('users', '/shugelab/users'), ('lee', '/shugelab/users/lee')]
        >>> path2hierarchy(path) == t1
        True
        >>> path2hierarchy('/') == [('index', '/~index')]
        True
    """
    caches = []

    if "/" == path:
        return [("index", "/~index")]
    elif "/" in path:
        parts = path.split('/')
        start = len(parts) - 2
        stop = -1
        step = -1
        for i in range(start, stop, step):
            name = parts[i + 1]
            links = "/%s" % "/".join(parts[1 : i + 2])
            if name == '':
                continue
            caches.append((name, links))

    caches.reverse()

    return caches

def text_path_to_button_path(path):
    buf = path2hierarchy(path)
    IS_ONLY_ONE_LEVEL = len(buf) == 1
    button_path = " / ".join(["[%s](%s/)" % (i[0], i[1]) for i in buf[:-1]])

    latest_level = buf[-1]
    path_name = latest_level[0]

    if IS_ONLY_ONE_LEVEL:
        button_path = path_name
    else:
        button_path = "%s / %s" % (button_path, path_name)

    return button_path


def md2html(config_agent, req_path, text, static_file_prefix, **view_settings):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = req_path_to_local_full_path(req_path = req_path, folder_pages_full_path = folder_pages_full_path)
    save_to_prefix = os.path.dirname(local_full_path)

    buf = text
    
    if tex2png:
        try:
            buf = macro_tex2md(buf, save_to_prefix = save_to_prefix, **view_settings)
        except Exception, ex:
            logging.error(str(ex))

            msg = "it seems that latex or dvipng doesn't works well on your box, or source code is invalid"
            logging.error(msg)

            buf = text

    if graphviz2png:
        try:
            buf = macro_graphviz2md(buf, save_to_prefix = save_to_prefix, **view_settings)
        except Exception, ex:
            logging.error(str(ex))

            msg = "it seems that graphviz doesn't works well on your box, or source code is invalid"
            logging.error(msg)

            buf = text

    if static_file_prefix:
        buf = convert_static_file_url(buf, static_file_prefix)

    buf = zw_macro2md(buf, folder_pages_full_path = folder_pages_full_path, req_path = req_path, **view_settings)

    buf = md_table.md_table2html(buf)
    buf = code_block_to_md_code(buf)
    buf = trac_wiki_code_block_to_md_code(buf)

    buf = markdown.markdown(buf)
    
    return buf


def test_path2hierarchy():
    for i in [
        ("/", [("index", "/~index")]), # name, link pairs

        ("/system-management/gentoo/abc",
         [("system-management", "/system-management"),("gentoo", "/system-management/gentoo"),("abc", "/system-management/gentoo/abc"),]),

        ("/programming-language",
         [("programming-language", "/programming-language"),]),

        ("/programming-language/",
         [("programming-language", "/programming-language"),]),
                                       ]:
        req_path = i[0]
        links = i[1]
        assert path2hierarchy(req_path) == links



def req_path_to_local_full_path(req_path, folder_pages_full_path):
    """
    >>> folder_pages_full_path = "/tmp/pages/"
    >>> req_path_to_local_full_path("sandbox1", folder_pages_full_path)
    '/tmp/pages/sandbox1.md'

    >>> req_path_to_local_full_path("sandbox1/", folder_pages_full_path)
    '/tmp/pages/sandbox1/'

    >>> req_path_to_local_full_path("hacking/fetion/fetion-protocol/", folder_pages_full_path)
    '/tmp/pages/hacking/fetion/fetion-protocol/'

    >>> req_path_to_local_full_path("hacking/fetion/fetion-protocol/method-option.md", folder_pages_full_path)
    '/tmp/pages/hacking/fetion/fetion-protocol/method-option.md'

    >>> req_path_to_local_full_path("~all", folder_pages_full_path)
    '/tmp/pages/'

    >>> req_path_to_local_full_path("/", folder_pages_full_path)
    '/tmp/pages/'

    >>> req_path_to_local_full_path("", folder_pages_full_path)
    '/tmp/pages/'
    """
    req_path = web.rstrips(req_path, ".md")
    req_path = web.rstrips(req_path, ".markdown")

    if req_path in consts.g_special_paths:
        return folder_pages_full_path

    elif not req_path.endswith("/"):
        HOME_PAGE = ""
        if req_path == HOME_PAGE:
            return folder_pages_full_path

        path_md = "%s.md" % os.path.join(folder_pages_full_path, req_path)
        path_markdown = "%s.markdown" % os.path.join(folder_pages_full_path, req_path)

        if os.path.exists(path_md):
            return path_md
        elif os.path.exists(path_markdown):
            return path_markdown
        else:
            return path_md

    elif req_path == "/":
        return folder_pages_full_path

    else:
        return os.path.join(folder_pages_full_path, req_path)


def get_title_by_file_path_in_md(folder_pages_full_path, file_path_suffix):
    prefix = os.path.join(folder_pages_full_path, file_path_suffix)
    a = prefix + ".md"
    b = prefix + ".markdown"

    if os.path.exists(a):
        local_full_path = a
    elif os.path.exists(b):
        local_full_path =  b
    else:
        return None

    buf = commons.shutils.cat(local_full_path)
    if buf:
        buf = commons.strip_bom(buf)

    p = '^#\s*(?P<title>.+?)\s*$'
    p_obj = re.compile(p, re.UNICODE | re.MULTILINE)
    match_obj = p_obj.search(buf)

    if match_obj:
        title = match_obj.group('title')
    else:
        title = None
    return title

def sequence_to_unorder_list(folder_pages_full_path, seq, **view_settings):
    """
        >>> sequence_to_unorder_list("", ['a','b','c'], show_full_path = 1)
        u'- [a](/a)\\n- [b](/b)\\n- [c](/c)'
    """
    lis = []
    for i in seq:
        i = web.utils.strips(i, "./")
        stripped_name = web.utils.rstrips(i, ".md")
        stripped_name = web.utils.rstrips(stripped_name, ".markdown")

        name, url = stripped_name, "/" + stripped_name
        if not view_settings["show_full_path"]:
            file_path_suffix = name
            buf = get_title_by_file_path_in_md(folder_pages_full_path, file_path_suffix)
            if buf is None:
                name = name.split('/')[-1].replace('-', ' ').title()
            else:
                name = buf

        lis.append('- [%s](%s)' % (name, url))

    buf = "\n".join(lis)
    buf = web.utils.safeunicode(buf)

    return buf

def macro_zw2md_ls(text, folder_pages_full_path, **view_settings):
    shebang_p = "#!zw"
    code_p = '(?P<code>[^\f\v]+?)'
    code_block_p = "^\{\{\{[\s]*%s*%s[\s]*\}\}\}" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        code = code.split("\n")[1]

        if code.startswith("ls("):
            p = 'ls\("(?P<path>.+?)",\s*maxdepth\s*=\s*(?P<maxdepth>\d+)\s*\)'
            m = re.match(p, code, re.UNICODE | re.MULTILINE)
            req_path = m.group("path")
            full_path = os.path.join(folder_pages_full_path, req_path)
            max_depth = int(m.group("maxdepth"))

            if os.path.exists(full_path):
                buf = shell.get_page_file_list_by_req_path(folder_pages_full_path = folder_pages_full_path,
                                                           req_path = req_path,
                                                           max_depth = max_depth)
                buf = sequence_to_unorder_list(folder_pages_full_path = folder_pages_full_path,
                                               seq = buf.split("\n"),
                                               **view_settings)
            else:
                buf = ""
            return buf

        buf_fixed = "{{{#!zw\n%s\n}}}" % code
        return buf_fixed
#        return code

    return p_obj.sub(code_repl, text)

def zw_macro2md(text, folder_pages_full_path, req_path, **view_settings):
    buf = text
    buf = macro_cat.macro_zw2md_cat(text = buf, folder_pages_full_path = folder_pages_full_path, req_path = req_path, **view_settings)
    buf = macro_zw2md_ls(text = buf, folder_pages_full_path = folder_pages_full_path, req_path = req_path, **view_settings)
    return buf


if __name__ == "__main__":
    import doctest
    doctest.testmod()

#    test_path2hierarchy()
