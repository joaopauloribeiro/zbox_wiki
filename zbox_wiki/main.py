#!/usr/bin/env python
#-*- coding:utf-8 -*-
import cgi
import os

# ship web.py with this project for walking around custom static files folder bug
import web

import acl
import consts
import commons
import page
import config_agent


# declare for using in scripts/fcgi_main.py
__all__ = [
    "main",
    "web",
    "mapping",
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

        # simple E-mail wrapper in CSS
        email = maintainer_email.replace("@", " &lt;AT&gt; ")
        buf = ro_tpl_p1 % email

        repo_url = config_agent.config.get("main", "repository_url")
        if repo_url:
            buf += "<pre><code>    git clone %s</code></pre>" % repo_url

        web.Forbidden.message = buf


class WikiPage(object):
    @acl.check_ip
    @acl.check_rw
    def GET(self, req_path):
        req_path = cgi.escape(req_path)

        inputs = web.input()
        action = inputs.get("action", "read")
        if action not in consts.g_actions:
            raise web.BadRequest()

        if action == "read":
            return page.wp_read(config_agent = config_agent, req_path = req_path, tpl_render = tpl_render)
        elif action == "update":
            return page.wp_update(config_agent = config_agent, req_path = req_path, tpl_render = tpl_render)
        elif action == "rename":
            return page.wp_rename(config_agent = config_agent, req_path = req_path, tpl_render = tpl_render)
        elif action == "delete":
            return page.wp_delete(config_agent = config_agent, req_path = req_path, tpl_render = tpl_render)
        elif action == "source":
            return page.wp_source(config_agent = config_agent, req_path = req_path, tpl_render = tpl_render)
        else:
            raise web.BadRequest()

    @acl.check_ip
    @acl.check_rw
    def POST(self, req_path):
        req_path = cgi.escape(req_path)

        inputs = web.input()
        action = inputs.get("action")
        if (not action) or (action not in ("update", "rename")):
            raise web.BadRequest()

        new_content = inputs.get("content")
        new_content = web.utils.safestr(new_content)

        if action == "update":
            if (req_path in consts.g_special_paths) or (req_path in consts.g_redirect_paths) or req_path.endswith("/"):
                raise web.BadRequest()

            return page.wp_update_post(config_agent = config_agent, req_path = req_path, new_content = new_content)

        elif action == "rename":
            new_path = inputs.get("new_path")
            if (req_path in consts.g_special_paths) or (req_path in consts.g_redirect_paths) or (not new_path):
                raise web.BadRequest()

            return page.wp_rename_post(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path, new_path = new_path)

        url = os.path.join("/", req_path)
        web.redirect(url)
        return


class SpecialWikiPage(object):
    @acl.check_ip
    @acl.check_rw
    def GET(self, req_path):
        inputs = web.input()

        FIRST_PAGE = 0
        offset = int(inputs.get("offset", FIRST_PAGE))

        page_limit = config_agent.config.getint("pagination", "page_limit")
        limit = int(inputs.get("limit", page_limit))

        if req_path == "~recent":
            return page.wp_get_recent_changes_from_cache(config_agent = config_agent, tpl_render = tpl_render,
                                                         req_path = req_path, limit = limit, offset = offset)
        elif req_path == "~all":
            return page.wp_get_all_pages(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path,
                                         limit = limit, offset = offset)
        elif req_path == "~settings":
            return page.wp_view_settings(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path)

        elif req_path == "~stat":
            return page.wp_stat(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path)

        elif req_path == "~new":
            return page.wp_new(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path)

        else:
            return web.BadRequest()

    @acl.check_ip
    @acl.check_rw
    def POST(self, req_path):
        inputs = web.input()
            
        if req_path == "~search":
            return page.wp_search(config_agent = config_agent, tpl_render = tpl_render, req_path = req_path)

        elif req_path == "~settings":
            show_full_path = inputs.get("show_full_path")
            auto_toc = inputs.get("auto_toc")
            highlight_code = inputs.get("highlight_code")

            if show_full_path == "on":
                show_full_path = 1
            else:
                show_full_path = 0
            web.setcookie(name = "zw_show_full_path", value = show_full_path, expires = 31536000)

            if auto_toc == "on":
                auto_toc = 1
            else:
                auto_toc = 0
            web.setcookie(name = "zw_auto_toc", value = auto_toc, expires = 31536000)

            if highlight_code == "on":
                highlight_code = 1
            else:
                highlight_code = 0
            web.setcookie(name = "zw_highlight", value = highlight_code, expires = 31536000)


            latest_req_path = web.cookies().get("zw_latest_req_path")

            if latest_req_path and (latest_req_path not in consts.g_redirect_paths) and latest_req_path != "/":
                web.setcookie(name = "zw_latest_req_path", value = "", expires = -1)
                latest_req_path = "/" + latest_req_path
            else:
                latest_req_path = "/"

            return web.seeother(latest_req_path)

        elif req_path == "~new":
            buf_path = inputs.get("path")
            buf_path = commons.strutils.lstrips(buf_path, "/")
            buf_path = commons.strutils.rstrips(buf_path, ".md")
            fixed_path = commons.strutils.rstrips(buf_path, ".markdown")
            if (not fixed_path) or (fixed_path in consts.g_special_paths) or (fixed_path in consts.g_redirect_paths):
                raise web.BadRequest()

            content = inputs.get("content")
            content = web.utils.safestr(content)
            if not content:
                raise web.BadRequest()

            page.wp_create(config_agent = config_agent, req_path = req_path, path = fixed_path, content = content)
            return

        else:
            raise web.NotFound()


class Robots(object):
    def GET(self):
        folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
        path = os.path.join(folder_pages_full_path, "robots.txt")
        content = commons.shutils.cat(path)

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

    if os.path.islink(dst_full_path) and os.readlink(dst_full_path) != src_full_path:
        if os.path.islink(dst_full_path):
            os.remove(dst_full_path)

    if not os.path.exists(dst_full_path):
        os.symlink(src_full_path, dst_full_path)

def main(instance_root_full_path):
    web.config.static_path = config_agent.get_full_path("paths", "static_path")

    fix_pages_path_symlink(instance_root_full_path)
    fix_403_msg()

    setup_session_folder_full_path()
    app.run()

