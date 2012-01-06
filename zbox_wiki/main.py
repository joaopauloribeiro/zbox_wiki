#!/usr/bin/env python
#-*- coding:utf-8 -*-
import cgi
import functools
import os
import re
import shutil
import sys
import web

import commons
try:
    import conf
except ImportError:
    import default_conf as conf

__all__ = [
    "start",
]


web.config.debug = conf.debug
web.config.static_path = conf.static_path


urls = (
    "/robots.txt", "Robots",
    "/~([a-zA-Z0-9_\-/.]+)", "SpecialWikiPage",
    ur"/([a-zA-Z0-9_\-/.%s]*)" % commons.CJK_RANGE, "WikiPage",
)

app = web.application(urls, globals())

t_render = web.template.render(conf.templates_path)

#def config_template_and_session():
#    if not web.config.get("_session"):
#        session = web.session.Session(app, web.session.DiskStore(conf.sessions_path), initializer={"username": None})
#        web.config._session = session
#    else:
#        session = web.config._session
#
#    t_globals = {
#        "utils" : web.utils,
#        "session" : session,
#        "ctx" : web.ctx
#        }
#    t_render = web.template.render(conf.templates_path, globals=t_globals)
#
#    def session_hook():
#        web.ctx.session = session
#        web.template.Template.globals["session"] = session
#    app.add_processor(web.loadhook(session_hook))


def _check_ip(*args, **kwargs):
    # allow_ips = ("192.168.0.10", )
    allow_ips = None
    remote_ip = web.ctx["ip"]

    if not commons.ip_in_network_ranges(remote_ip, allow_ips):
        return False

    return True

def check_ip(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _check_ip(*args, **kwargs):
            return f(*args, **kwargs)
        raise web.Forbidden()
    return wrapper


def _check_acl(*args, **kwargs):
    inputs = web.input()
    action = inputs.get("action", "read")

    if conf.readonly:
        if action not in ("read", "source"):
            return False

    return True

def check_acl(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        if _check_acl(*args, **kwargs):
            return f(*args, **kwargs)
        raise web.Forbidden()
    return wrapper



if conf.maintainer_email:
    msg = "This wiki is READONLY." + "<br />"
    msg += "Maintainer: " + conf.maintainer_email_prefix + " &lt;AT&gt; " + conf.maintainer_email_suffix + "<br />"
    msg += "<br />"

    if conf.repository_url:
        msg += "You could fork it and commit changes, then send a pull request to maintainer." + "<br />"
        msg += "<pre><code> git clone %s </code></pre>" % conf.repository_url

    web.Forbidden.message = msg



def get_recent_change_list(limit, show_full_path = conf.show_full_path):
    """ return recent changed files in HTML text for rendering page '/~recent_changed'. """
    get_rc_list_cmd = " cd %s; find . -name '*.md' | xargs ls -t | head -n %d " % \
                      (conf.pages_path, limit)
    buf = os.popen(get_rc_list_cmd).read().strip()

    if buf:
        buf = web.utils.safeunicode(buf)
        lines = buf.split("\n")
        strips_seq_item = ".md"

        if show_full_path:
            callable_obj = None
        else:
            callable_obj = get_page_file_title

        return _sequence_to_unorder_list(lines, strips_seq_item, callable_obj=callable_obj)

def get_page_file_or_dir_full_path_by_req_path(req_path):
    """
    '/zbox-wiki/about-zboxwiki' -> '$PAGE_PATH/zbox-wiki/about-zboxwiki.md'
    '/zbox-wiki/' -> '$PAGE_PATH/zbox-wiki/'
    """
    if not req_path.endswith("/"):
        return "%s.md" % os.path.join(conf.pages_path, req_path)
    elif req_path == "/":
        return conf.pages_path
    else:
        return os.path.join(conf.pages_path, req_path)

def get_page_file_title(req_path):
    """
        >>> get_page_file_title('application/air/run-air-application-on-gentoo')
        'run air application on gentoo'
    """
    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)
    c = commons.cat(full_path)

    p = '^#\s(?P<title>.+?)\s$'
    p_obj = re.compile(p, re.MULTILINE)
    match_obj = p_obj.search(c)
    if match_obj:
        title = match_obj.group('title')
    elif '/' in req_path:
        title = req_path.split('/')[-1].replace('-', ' ')
    else:
        title = 'untitled'

    return title

def get_dot_idx_content_by_full_path(full_path):
    dot_idx_full_path = os.path.join(full_path, ".index.md")
    return commons.cat(dot_idx_full_path)

def get_page_file_list_content_by_full_path(full_path, show_full_path = conf.show_full_path):
    """ return files list in specify full path in HTML text """
    req_path = full_path.replace(conf.pages_path, "")
    req_path = web.utils.strips(req_path, "/")

    tree_cmd = " cd %s; find %s -name '*.md' \! -name '.index.md' " % (conf.pages_path, req_path)
    buf = os.popen(tree_cmd).read().strip()

    if buf:
        buf = web.utils.safeunicode(buf)
        lines = buf.split("\n")
        strips_seq_item = ".md"

        if show_full_path:
            callable_obj = None
        else:
            callable_obj = get_page_file_title

        return _sequence_to_unorder_list(lines = lines,
                                        strips_seq_item = strips_seq_item,
                                        callable_obj = callable_obj)

def delete_page_file_by_full_path(full_path):
    if os.path.isfile(full_path):
        os.remove(full_path)
        return True
    elif os.path.isdir(full_path):
        idx_dot_md = os.path.join(full_path, ".index.md")
        os.remove(idx_dot_md)
        return True
    return False

def get_page_file_index(limit = conf.index_page_limit, show_full_path = conf.show_full_path):
    """ return all files list in HTML text for rendering page '/index'. """
    get_page_file_index_cmd = " cd %s; find . -name '*.md' | head -n %d " % (conf.pages_path, limit)
    buf = os.popen(get_page_file_index_cmd).read().strip()
    if buf:
        buf = web.utils.safeunicode(buf)
        lines = buf.split("\n")

        if show_full_path:
            callable_obj = None
        else:
            callable_obj = get_page_file_title

        content = _sequence_to_unorder_list(lines, strips_seq_item=".md", callable_obj=callable_obj)
        return content

def _sequence_to_unorder_list(lines, strips_seq_item=None, callable_obj=None):
    """
        >>> _sequence_to_unorder_list(['a','b','c'])
        '- [a](/a)\\n- [b](/b)\\n- [c](/c)'
    """
    lis = []

    for i in lines:
        name = web.utils.strips(i, "./")
        if strips_seq_item:
            name = web.utils.strips(name, strips_seq_item)

        url = os.path.join("/", name)
        if callable_obj:
            name = apply(callable_obj, (name, ))
        lis.append('- [%s](%s)' % (name, url))

    content = "\n".join(lis)
    content = web.utils.safeunicode(content)

    return content

def search_by_filename_and_file_content(keywords,
                                        limit = conf.search_page_limit,
                                        show_full_path = conf.show_full_path):
    """
    Following doesn't works if cmd contains pipe character:

        p_obj = subprocess.Popen(shlex.split(cmd), stdout=subprocess.PIPE)
        p_obj.wait()
        resp = p_obj.stdout.read().strip()

    So we have to do use deprecated syntax ```os.popen```, for more detail, see
    http://stackoverflow.com/questions/89228/how-to-call-external-command-in-python .
    """

    find_by_filename_matched = " -o -name ".join([" '*%s*' " % i for i in keywords.split()])
    find_by_content_matched = " \| ".join(keywords.split())
    is_multiple_keywords = find_by_content_matched.find("\|") != -1

    if is_multiple_keywords:
        find_by_filename_cmd = " cd %s; "\
                               " find . \( -name %s \) -type f | " \
                               " grep '.md$' | head -n %d " % \
                               (conf.pages_path, find_by_filename_matched, limit)

        find_by_content_cmd = " cd %s; " \
                              " grep ./ --recursive --ignore-case --include='*.md' --regexp ' \(%s\) ' | " \
                              " awk -F ':' '{print $1}' | uniq | head -n %d " % \
                              (conf.pages_path, find_by_content_matched, limit)
    else:
        find_by_filename_cmd = " cd %s; " \
                               " find . -name %s -type f | " \
                               " grep '.md$' | head -n %d " % \
                               (conf.pages_path, find_by_filename_matched, limit)

        find_by_content_cmd = " cd %s; " \
                              " grep ./ --recursive --ignore-case --include='*.md' --regexp '%s' | " \
                              " awk -F ':' '{print $1}' | uniq | head -n %d " % \
                              (conf.pages_path, find_by_content_matched, limit)

    if web.config.debug:
        msg = "find by filename >>> " + find_by_filename_cmd
        sys.stdout.write("\n" + msg + "\n")

    if web.config.debug:
        msg = "find by content >>> " + find_by_content_cmd
        sys.stdout.write("\n" + msg + "\n")


    matched_content_lines = os.popen(find_by_content_cmd).read().strip()
    matched_content_lines = web.utils.safeunicode(matched_content_lines)
    if matched_content_lines:
        matched_content_lines = web.utils.safeunicode(matched_content_lines)
        matched_content_lines = matched_content_lines.split("\n")

    matched_filename_lines = os.popen(find_by_filename_cmd).read().strip()
    matched_filename_lines = web.utils.safeunicode(matched_filename_lines)
    if matched_filename_lines:
        matched_filename_lines = web.utils.safeunicode(matched_filename_lines)
        matched_filename_lines = matched_filename_lines.split("\n")

    if matched_content_lines and matched_filename_lines:
        # NOTICE: build-in function set() doesn't keep order, we shouldn't use it.
        # mixed = set(matched_filename_lines)
        # mixed.update(set(matched_content_lines))
        mixed = web.utils.uniq(matched_filename_lines + matched_content_lines)
    elif matched_content_lines and not matched_filename_lines:
        mixed = matched_content_lines
    elif not matched_content_lines  and matched_filename_lines:
        mixed = matched_filename_lines
    else:
        return None

    lines = mixed

    if show_full_path:
        callable_obj = None
    else:
        callable_obj = get_page_file_title

    content = _sequence_to_unorder_list(lines, strips_seq_item=".md", callable_obj=callable_obj)

    return content

special_path_mapping = {
    "index" : get_page_file_index,
    "s" : search_by_filename_and_file_content,
}

def _append_static_file(text, filepath, file_type, add_newline=False):
    assert file_type in ("css", "js")

    if file_type == "css":
        ref = '<link href="%s" rel="stylesheet" type="text/css">' % filepath
    else:
        ref = '<script type="text/javascript" src="%s"></script>' % filepath

    if not add_newline:
        static_files = "%s\n    %s" % (text, ref)
    else:
        static_files = "%s\n\n    %s" % (text, ref)

    return static_files

#def _get_trac_wiki_theme():
#    static_files = ""
#    css_files = ["trac.css", "wiki.css"]
#
#    for i in css_files:
#        filepath = os.path.join("/static", "css", i)
#        static_files = _append_static_file(static_files, filepath, file_type = "css")
#
#    return static_files

def get_global_static_files(auto_toc = conf.auto_toc,
                            highlight = conf.highlight,
                            reader_mode = conf.reader_mode):
    static_files = ""

    css_files = ("zw-base.css",)
    for i in css_files:
        path = os.path.join("/static", "css", i)
        static_files = _append_static_file(static_files, path, file_type = "css")

    if reader_mode:
        path = os.path.join("/static", "css", "zw-reader.css")
        static_files = _append_static_file(static_files, path, file_type = "css")

    if auto_toc:
        path = os.path.join("/static", "css", "zw-toc.css")
        static_files = _append_static_file(static_files, path, file_type = "css")

        
    if highlight:
        path = os.path.join("/static", "js", "prettify", "prettify.css")
        static_files = _append_static_file(static_files, path, file_type = "css", add_newline = True)


    static_files = "%s\n" % static_files

    js_files = ("jquery.js", "jquery-ui.js")
    static_files += "\n"
    for i in js_files:
        path = os.path.join("/static", "js", i)
        static_files = _append_static_file(static_files, path, file_type = "js")

    js_files = ("zw-base.js", )
    static_files += "\n"
    for i in js_files:
        path = os.path.join("/static", "js", i)
        static_files = _append_static_file(static_files, path, file_type = "js")


    if auto_toc:
        static_files += "\n"
        path = os.path.join("/static", "js", "zw-toc.js")
        static_files = _append_static_file(static_files, path, file_type = "js")

    if highlight:
        static_files += "\n"
        js_files = (os.path.join("prettify", "prettify.js"), "highlight.js")
        for i in js_files:
            path = os.path.join("/static", "js", i)
            static_files = _append_static_file(static_files, path, file_type = "js")

    return static_files

def get_the_same_folders_cssjs_files(req_path):
    # NOTICE: this features doesn't works on file system mounted by sshfs.

    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)
    if os.path.isfile(full_path):
        work_path = os.path.dirname(full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))
    elif os.path.isdir(full_path):
        work_path = full_path
        static_file_prefix = os.path.join("/static/pages", req_path)
    else:
        # special page, such as '/~index'
        work_path = conf.pages_path
        static_file_prefix = "/static/pages"

    iters = os.listdir(work_path)
    cssjs_files = [i for i in iters
                   if (not i.startswith(".")) and (i.endswith(".js") or i.endswith(".css"))]

    if not cssjs_files:
        return ""

    css_buf = ""
    js_buf = ""
    for i in cssjs_files:
        if i.endswith(".css"):
            path = os.path.join(static_file_prefix, i)
            css_buf = _append_static_file(css_buf, path, file_type = "css")
        elif i.endswith(".js"):
            path = os.path.join(static_file_prefix, i)
            js_buf = _append_static_file(js_buf, path, file_type = "js")

    return "%s\n    %s" % (css_buf, js_buf)

def wp_read_recent_change():
    inputs = web.input()
    limit = inputs.get("limit")

    show_full_path = inputs.get("show_full_path") or conf.show_full_path
    if show_full_path == "0":
        show_full_path = False

    title = "Recent Changes"
    static_file_prefix = "/static/pages"
    req_path = title

    if limit:
        limit = int(limit) or conf.index_page_limit
        content = get_recent_change_list(limit, show_full_path=show_full_path)
    else:
        content = get_recent_change_list(conf.index_page_limit, show_full_path=show_full_path)

    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    if content:
        content = commons.md2html(text = content,
                                  work_full_path = full_path,
                                  static_file_prefix = static_file_prefix)
    else:
        content = "Not found"

    static_files = get_global_static_files()
    # static_files = "%s\n    %s" % (static_files, get_the_same_folders_cssjs_files(req_path))
    assert static_files != None

    return t_render.canvas(conf = conf,
                           req_path = req_path,
                           title = title,
                           content = content,
                           toolbox = False,
                           static_files = static_files)

def wp_read(req_path):
    inputs = web.input()

    show_full_path = inputs.get("show_full_path", True)
    if show_full_path == "0":
        show_full_path = False

    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    if conf.button_mode_path:
        buf = commons.text_path2btns_path("/%s" % req_path)
        title = commons.md2html(buf)
    else:
        title = req_path

    if os.path.isfile(full_path):
        work_full_path = os.path.dirname(full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))

        content = commons.cat(full_path)
    elif os.path.isdir(full_path):
        work_full_path = full_path
        static_file_prefix = os.path.join("/static/pages", req_path)

        dot_idx_content = get_dot_idx_content_by_full_path(full_path)
        page_file_list_content = get_page_file_list_content_by_full_path(full_path,
                                                                        show_full_path=show_full_path)
        content = ""

        if dot_idx_content:
            content = dot_idx_content
        if page_file_list_content:
            content = "%s\n\n----\n%s" % (content, page_file_list_content)
    else:
        web.seeother("/%s?action=edit" % req_path)
        return

    content = commons.md2html(text=content,
                                       work_full_path=work_full_path,
                                       static_file_prefix=static_file_prefix)

    static_files = get_global_static_files()
    static_files = "%s\n    %s" % (static_files, get_the_same_folders_cssjs_files(req_path))

    return t_render.canvas(conf = conf,
                           req_path=req_path,
                           title=title,
                           content=content,
                           static_files=static_files)

def wp_edit(req_path):
    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    if conf.button_mode_path:
        buf = commons.text_path2btns_path("/%s" % req_path)
        title = commons.md2html(buf)
    else:
        title = req_path

    if os.path.isfile(full_path):
        content = commons.cat(full_path)
    elif os.path.isdir(full_path):
        content = get_dot_idx_content_by_full_path(full_path)
    elif not os.path.exists(full_path):
        content = ""
    else:
        raise Exception("unknow path")

    static_files = get_global_static_files(auto_toc = False,
                            highlight = False,
                            reader_mode = False)

    return t_render.editor(req_path, title, content, static_files=static_files)

def wp_rename(req_path):
    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    if not os.path.exists(full_path):
        raise web.NotFound()

    return t_render.rename(req_path, static_files = get_global_static_files())

def wp_delete(req_path):
    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    delete_page_file_by_full_path(full_path)

    web.seeother("/")
    return


def wp_source(req_path):
    full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

    if os.path.isdir(full_path):
        web.header("Content-Type", "text/plain")
        return "this is a black hole"

    elif os.path.isfile(full_path):
        web.header("Content-Type", "text/plain")
        return commons.cat(full_path)

    else:
        raise web.BadRequest()


class WikiPage:
    @check_ip
    @check_acl
    def GET(self, req_path):
        req_path = cgi.escape(req_path)
        inputs = web.input()
        action = inputs.get("action", "read")

        assert action in ("edit", "read", "rename", "delete", "source")

        if action == "read":
            if req_path == "":
                return wp_read_recent_change()
            else:
                return wp_read(req_path)
        elif action == "edit":
            return wp_edit(req_path)
        elif action == "rename":
            return wp_rename(req_path)
        elif action == "delete":
            return wp_delete(req_path)
        elif action == "source":
            return wp_source(req_path)

        raise web.BadRequest()

    @check_ip
    @check_acl
    def POST(self, req_path):
        req_path = cgi.escape(req_path)
        inputs = web.input()
        action = inputs.get("action")

        if action and action not in ("edit", "rename"):
            raise web.BadRequest()

        content = inputs.get("content")
        content = web.utils.safestr(content)

        # NOTICE: if req_path == `users/`, full_path will be `/path/to/users/`,
        # parent will be `/path/to/users`.

        full_path = get_page_file_or_dir_full_path_by_req_path(req_path)

        parent = os.path.dirname(full_path)
        if not os.path.exists(parent):
            os.makedirs(parent)

        if action == "edit":
            if not os.path.isdir(full_path):
                web.utils.safewrite(full_path, content.replace("\r\n", "\n"))
            else:
                idx_dot_md_full_path = os.path.join(full_path, ".index.md")
                web.utils.safewrite(idx_dot_md_full_path, content.replace("\r\n", "\n"))

            web.seeother("/%s" % req_path)
        elif action == "rename":
            new_path = inputs.get("new_path")
            if not new_path:
                raise web.BadRequest()

            old_full_path = get_page_file_or_dir_full_path_by_req_path(req_path)
            if os.path.isfile(old_full_path):
                new_full_path = get_page_file_or_dir_full_path_by_req_path(new_path)
            elif os.path.isdir(old_full_path):
                new_full_path = os.path.join(conf.pages_path, new_path)
            else:
                raise Exception("unknow path")

            if os.path.exists(new_full_path):
                err_info = "Warning: The page foobar already exists."
                return t_render.rename(req_path, err_info, static_files = get_global_static_files())

            parent = os.path.dirname(new_full_path)
            if not os.path.exists(parent):
                os.makedirs(parent)

            shutil.move(old_full_path, new_full_path)

            if os.path.isfile(new_full_path):
                web.seeother("/%s" % new_path)
            elif os.path.isdir(new_full_path):
                web.seeother("/%s/" % new_path)

            return

        url = os.path.join("/", req_path)
        web.redirect(url)


class SpecialWikiPage:
    @check_ip
    @check_acl
    def GET(self, req_path):
        f = special_path_mapping.get(req_path)

        if not f:
            raise web.NotFound()

        inputs = web.input()
        show_full_path = inputs.get("show_full_path") or conf.show_full_path
        if show_full_path == "0":
            show_full_path = False

        limit = inputs.get("limit", conf.index_page_limit)
        if limit:
            limit = int(limit)

        if req_path == "index":
            content = get_page_file_index(limit=limit, show_full_path=show_full_path)
            content = commons.md2html(content)

            static_files = get_global_static_files()
            static_files = "%s\n    %s" % (static_files, get_the_same_folders_cssjs_files(req_path))

            req_path = "~index"
            title = "Index"
            return t_render.canvas(conf = conf,
                                   req_path=req_path,
                                   title=title,
                                   content=content,
                                   toolbox=False,
                                   static_files=static_files)


    @check_ip
    @check_acl
    def POST(self, req_path):
        f = special_path_mapping.get(req_path)
        inputs = web.input()

        if not f:
            raise web.NotFound()

        keywords = inputs.get("k")
        keywords = web.utils.safestr(keywords)

        if not keywords:
            raise web.BadRequest()

        limit = inputs.get("limit", conf.search_page_limit)
        if limit:
            limit = int(limit)

        content = search_by_filename_and_file_content(keywords, limit=limit)

        if content:
            content = commons.md2html(content)
        else:
            content = "not found matched"

        return t_render.search(keywords = keywords, content = content,
                               static_files = get_global_static_files())


class Robots:
    def GET(self):
        path = os.path.join(conf.pages_path, "robots.txt")
        content = commons.cat(path)

        web.header("Content-Type", "text/plain")
        return content

def start():
    app.run()


if __name__ == "__main__":
#    import sys
#    sys.stderr = file(conf.error_log, "a")
#    sys.stdout = file(conf.info_log, "a")

    #
    # run it in WSGI mode,
    # see also http://webpy.org/cookbook/fastcgi-nginx
    #
    web.wsgi.runwsgi = lambda func, addr=None: web.wsgi.runfcgi(func, addr)
    app.run()