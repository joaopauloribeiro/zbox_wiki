#!/usr/bin/env python
#-*- coding:utf-8 -*-
import cgi
import os
import shutil

import acl
import cache
import commons
import page
import config_agent
import paginator
import search
import static_file
import web
import mdutils


__all__ = [
    "web",

    "app",
    "mapping",
    "main",
    "fix_pages_path_symlink",

    "Robots",
    "SpecialWikiPage",
    "WikiPage",
]


mapping = (
    "/robots.txt", "Robots",
    "/favicon.ico", "FaviconICO",
    "/(~[a-zA-Z0-9_\-/.]+)", "SpecialWikiPage",
    ur"/([a-zA-Z0-9_\-/.%s]*)" % commons.CJK_RANGE, "WikiPage",
)

g_redirect_paths = ("favicon.ico", "robots.txt")
g_special_paths = ("~all", "~recent", "~search", "~settings", "~stat", "~new")
g_actions = ("edit", "read", "rename", "delete", "source")

app = web.application(mapping, globals())
folder_templates_full_path = config_agent.get_full_path("paths", "templates_path")
tpl_render = web.template.render(folder_templates_full_path)


def setup_session_folder_full_path():
    global session

    if not web.config.get("_session"):
        folder_sessions_full_path = config_agent.get_full_path("paths", "sessions_path")
        session = web.session.Session(app, web.session.DiskStore(folder_sessions_full_path), initializer = {"username": None})
        web.config._session = session
    else:
        session = web.config._session


def fix_403_msg():
    maintainer_email = config_agent.config.get("main", "maintainer_email")

    if maintainer_email:
        ro_tpl_p1 = """Page you request doesn't exists, and this wiki is READONLY. <br />
You could fork it and commit the changes, then send a pull request to the maintainer: <br />

<pre><code>%s</code></pre>"""

        # simple wrapper in CSS
        email = maintainer_email.replace("@", " &lt;AT&gt; ")
        buf = ro_tpl_p1 % email

        repo_url = config_agent.config.get("main", "repository_url")
        if repo_url:
            buf += "<pre><code>    git clone %s</code></pre>" % repo_url

        web.Forbidden.message = buf


def wp_view_settings():
    enable_show_full_path = web.cookies().get("zw_show_full_path", config_agent.config.get("frontend", "enable_show_full_path"))
    enable_show_full_path = int(enable_show_full_path)

    enable_auto_toc = web.cookies().get("zw_auto_toc", config_agent.config.getboolean("frontend", "enable_auto_toc"))
    enable_auto_toc = int(enable_auto_toc)

    enable_highlight = web.cookies().get("zw_highlight", config_agent.config.get("frontend", "enable_highlight"))
    enable_highlight = int(enable_highlight)

    return tpl_render.view_settings(enable_show_full_path = enable_show_full_path,
                                    enable_auto_toc = enable_auto_toc,
                                    enable_highlight = enable_highlight,
                                    static_files = static_file.g_global_static_files)


def wp_get_all_pages(enable_show_full_path, limit, offset):
    buf = cache.get_all_pages_list_from_cache()
    all_lines = buf.split()
    total_lines = len(all_lines)

    title = "All Pages List (%d/%d)" % (offset, total_lines / limit)

    start = offset * limit
    end = start + limit
    lines = all_lines[start : end]

    buf = mdutils.sequence_to_unorder_list(lines, enable_show_full_path = enable_show_full_path)
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    content = mdutils.md2html(text = buf, work_full_path = folder_pages_full_path)

    pg = paginator.Paginator()
    pg.total = total_lines
    pg.current_offset = offset
    pg.limit = limit
    pg.url = "/~all"

    return tpl_render.canvas(config = config_agent.config,
                             button_path = title,
                             content = content,
                             static_files = static_file.g_global_static_files,
                             paginator = pg)


class WikiPage(object):
    @acl.check_ip
    @acl.check_rw
    def GET(self, req_path):
        req_path = cgi.escape(req_path)

        inputs = web.input()
        action = inputs.get("action", "read")
        if action not in g_actions:
            raise web.BadRequest()

        show_Full_path_def = config_agent.config.getboolean("frontend", "enable_show_full_path")
        auto_toc_def = config_agent.config.getboolean("frontend", "enable_auto_toc")
        highlight_def = config_agent.config.getboolean("frontend", "enable_highlight")

        enable_show_full_path = int(web.cookies().get("zw_show_full_path", show_Full_path_def))
        enable_auto_toc = int(web.cookies().get("zw_auto_toc", auto_toc_def))
        enable_highlight = int(web.cookies().get("zw_highlight", highlight_def))

        if action == "read":
            if req_path == "":
                req_path = "home"

            return page.wp_read(req_path = req_path,
                                     enable_show_full_path = enable_show_full_path,
                                     enable_auto_toc = enable_auto_toc,
                                     enable_highlight = enable_highlight)
        elif action == "edit":
            return page.wp_edit(req_path)
        elif action == "rename":
            return page.wp_rename(req_path)
        elif action == "delete":
            return page.wp_delete(req_path)
        elif action == "source":
            return page.wp_source(req_path)
        else:
            raise web.BadRequest()

    @acl.check_ip
    @acl.check_rw
    def POST(self, req_path):
        req_path = cgi.escape(req_path)

        inputs = web.input()
        action = inputs.get("action")
        if (not action) or (action not in ("edit", "rename")):
            raise web.BadRequest()

        content = inputs.get("content")
        content = web.utils.safestr(content)

        # NOTICE: if req_path == `users/`, full_path will be `/path/to/users/`,
        #         its parent will be `/path/to/users`.
        full_path = mdutils.req_path_to_full_path(req_path)

        parent = os.path.dirname(full_path)
        if not os.path.exists(parent):
            os.makedirs(parent)

        if action == "edit":
            page.update_page_by_req_path(req_path = req_path, content = content)

            web.seeother("/%s" % req_path)
            return
        elif action == "rename":
            new_path = inputs.get("new_path")
            if not new_path:
                raise web.BadRequest()

            old_full_path = mdutils.req_path_to_full_path(req_path)
            if os.path.isfile(old_full_path):
                new_full_path = mdutils.req_path_to_full_path(new_path)
            elif os.path.isdir(old_full_path):
                folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
                new_full_path = os.path.join(folder_pages_full_path, new_path)
            else:
                raise Exception("un-expected path '%s'" % req_path)

            if os.path.exists(new_full_path):
                err_info = "WARNING: The page %s already exists" % new_full_path
                return tpl_render.rename(req_path, err_info, static_files = static_file.g_global_static_files)

            parent = os.path.dirname(new_full_path)
            if not os.path.exists(parent):
                os.makedirs(parent)

            shutil.move(old_full_path, new_full_path)

            cache.update_all_pages_list_cache()
            cache.update_recent_change_cache()

            if os.path.isfile(new_full_path):
                web.seeother("/%s" % new_path)
                return
            elif os.path.isdir(new_full_path):
                web.seeother("/%s/" % new_path)
                return
            else:
                raise Exception("un-expected path '%s'" % new_path)

        url = os.path.join("/", req_path)
        web.redirect(url)
        return


class SpecialWikiPage(object):
    @acl.check_ip
    @acl.check_rw
    def GET(self, req_path):
        assert req_path in g_special_paths

        inputs = web.input()
        FIRST_PAGE = 0
        offset = int(inputs.get("offset", FIRST_PAGE))

        page_limit = config_agent.config.getint("pagination", "page_limit")
        limit = int(inputs.get("limit", page_limit))

        enable_show_full_path = config_agent.config.getboolean("frontend", "enable_show_full_path")
        enable_show_full_path = int(web.cookies().get("zw_show_full_path", enable_show_full_path))

        if req_path == "~recent":
            return cache.wp_get_recent_changes_from_cache(enable_show_full_path = enable_show_full_path, limit = limit, offset = offset)
        elif req_path == "~all":
            return wp_get_all_pages(enable_show_full_path = enable_show_full_path, limit = limit, offset = offset)
        elif req_path == "~settings":
            return wp_view_settings()
        elif req_path == "~stat":
            return page.wp_stat()
        elif req_path == "~new":
            return page.wp_new()
        else:
            return web.BadRequest()

    @acl.check_ip
    @acl.check_rw
    def POST(self, req_path):
        inputs = web.input()
            
        if req_path == "~search":
            keywords = inputs.get("k")
            keywords = web.utils.safestr(keywords)
            if keywords:
                arg = web.cookies().get("zw_show_full_path") or config_agent.config.get("frontend", "enable_show_full_path")
                enable_show_full_path = int(arg)

                limit = config_agent.config.getint("pagination", "search_page_limit")
                lines = search.search_by_filename_and_file_content(keywords, limit = limit)
                content = mdutils.sequence_to_unorder_list(seq = lines, enable_show_full_path = enable_show_full_path)
            else:
                content = None

            if content:
                content = mdutils.md2html(content)
            else:
                content = "matched not found"

            return tpl_render.search(keywords = keywords, content = content, static_files = static_file.g_global_static_files)

        elif req_path == "~settings":
            enable_show_full_path = inputs.get("enable_show_full_path")
            enable_auto_toc = inputs.get("enable_auto_toc")
            enable_highlight = inputs.get("enable_highlight")

            if enable_show_full_path == "on":
                enable_show_full_path = 1
            else:
                enable_show_full_path = 0
            web.setcookie(name = "zw_show_full_path", value = enable_show_full_path, expires = 31536000)

            if enable_auto_toc == "on":
                enable_auto_toc = 1
            else:
                enable_auto_toc = 0
            web.setcookie(name = "zw_auto_toc", value = enable_auto_toc, expires = 31536000)

            if enable_highlight == "on":
                enable_highlight = 1
            else:
                enable_highlight = 0
            web.setcookie(name = "zw_highlight", value = enable_highlight, expires = 31536000)


            latest_req_path = web.cookies().get("zw_latest_req_path")

            if latest_req_path and (latest_req_path not in g_redirect_paths) and latest_req_path != "/":
                web.setcookie(name = "zw_latest_req_path", value = "", expires = -1)
                latest_req_path = "/" + latest_req_path
            else:
                latest_req_path = "/"

            web.seeother(latest_req_path)
            return
        elif req_path == "~new":
            real_req_path = inputs.get("path")
            fixed_req_path = web.lstrips(real_req_path, "/")

            content = inputs.get("content")
            content = web.utils.safestr(content)
        
            page.update_page_by_req_path(req_path = fixed_req_path, content = content)

            cache.update_recent_change_cache()
            cache.update_all_pages_list_cache()

            web.seeother(real_req_path)
            return
        else:
            raise web.NotFound()


class Robots(object):
    def GET(self):
        folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
        path = os.path.join(folder_pages_full_path, "robots.txt")
        content = commons.cat(path)

        web.header("Content-Type", "text/plain")
        return content


class FaviconICO(object):
   def GET(self):
       folder_static_full_path = config_agent.get_full_path("paths", "static_path")
       path = os.path.join(folder_static_full_path, "favicon.ico")

       if not os.path.exists(path):
           raise web.NotFound()

       with open(path) as f:
           content = f.read()

       web.header("Content-Type", "image/vnd.microsoft.icon")
       return content


def fix_pages_path_symlink(proj_root_full_path):
    src_full_path = os.path.join(proj_root_full_path, "pages")
    dst_full_path = os.path.join(proj_root_full_path, "static", "pages")

    if os.path.islink(dst_full_path):
        os.remove(dst_full_path)
        
    if not os.path.exists(dst_full_path):
        os.symlink(src_full_path, dst_full_path)


def main(instance_root_full_path):
    web.config.debug = config_agent.config.getboolean("main", "debug")
    web.config.static_path = config_agent.get_full_path("paths", "static_path")

    fix_pages_path_symlink(instance_root_full_path)
    fix_403_msg()

    setup_session_folder_full_path()
    app.run()

