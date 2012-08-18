import logging
import os
import web

import cache
import commons
import config_agent
import mdutils
import static_file


logging.getLogger("page").setLevel(logging.DEBUG)

folder_templates_full_path = config_agent.get_full_path("paths", "templates_path")
tpl_render = web.template.render(folder_templates_full_path)


def get_dot_idx_content_by_full_path(full_path):
    dot_idx_full_path = os.path.join(full_path, ".index.md")
    return commons.cat(dot_idx_full_path)


def get_page_file_list_by_req_path(req_path, sort_by_modified_ts = False, max_depth = None, limit = None, folder_pages_full_path = None):
    if req_path in ("~all", "~recent"):
        req_path = "."
    else:
        req_path = web.utils.strips(req_path, "/")

    if folder_pages_full_path is None:
        folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")

    if max_depth is None:
        cmd = " cd %s; find %s -follow -name '*.md' -or -name '*.markdown'  " % \
            (folder_pages_full_path, req_path)
    else:
        cmd = " cd %s; find %s -maxdepth %d -follow -name '*.md' -or -name '*.markdown'  " % \
            (folder_pages_full_path, req_path, max_depth)

    cmd += " | grep -v  -E '(.index.md|.index.markdown)' "

    if sort_by_modified_ts:
        cmd += " | xargs ls -t "

    if limit is not None:
        cmd += " | head -n %d " % limit

    logging.info(cmd)

    buf = os.popen(cmd).read().strip()

    return buf

def delete_page_file_by_full_path(full_path):
    if os.path.isfile(full_path):
        os.remove(full_path)
        return True
    elif os.path.isdir(full_path):
        idx_dot_md = os.path.join(full_path, ".index.md")
        os.remove(idx_dot_md)
        return True
    return False

def get_the_same_folders_cssjs_files(req_path):
    """ NOTICE: this features doesn't works on file system mounted by sshfs. """
    full_path = mdutils.req_path_to_full_path(req_path)

    if os.path.isfile(full_path):
        work_path = os.path.dirname(full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))
    elif os.path.isdir(full_path):
        work_path = full_path
        static_file_prefix = os.path.join("/static/pages", req_path)
    elif req_path == "home":
        work_path = os.path.dirname(full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))
    else:
        # special page, such as '/~index'
        folder_page_full_path = config_agent.get_full_path("paths", "pages_path")
        work_path = folder_page_full_path
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
            css_buf = static_file.append_static_file(css_buf, path, file_type = "css")
        elif i.endswith(".js"):
            path = os.path.join(static_file_prefix, i)
            js_buf = static_file.append_static_file(js_buf, path, file_type = "js")

    return "%s\n    %s" % (css_buf, js_buf)



def update_page_by_req_path(req_path, content):
    full_path = mdutils.req_path_to_full_path(req_path)

    if full_path.endswith((".md", ".markdown")):
        folder_parent = os.path.dirname(full_path)
        if not os.path.exists(folder_parent):
            os.makedirs(folder_parent)

    if not os.path.isdir(full_path):
        web.utils.safewrite(full_path, content.replace("\r\n", "\n"))
    else:
        idx_dot_md_full_path = os.path.join(full_path, ".index.md")
        web.utils.safewrite(idx_dot_md_full_path, content.replace("\r\n", "\n"))


def wp_read(req_path, enable_show_full_path, enable_auto_toc, enable_highlight,
            pages_path = None,
            enable_show_quick_links = None,
            enable_show_source_button = None,
            enable_show_home_link = None):

    if enable_show_quick_links is None:
        enable_show_quick_links = config_agent.config.getboolean("frontend", "enable_show_quick_links")
    if enable_show_source_button is None:
        enable_show_source_button = config_agent.config.getboolean("frontend", "enable_show_source_button"),
    if enable_show_home_link is None:
        enable_show_home_link = config_agent.config.getboolean("frontend", "enable_show_home_link")

    if pages_path is None:
        folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    else:
        folder_pages_full_path = pages_path

    if config_agent.config.getboolean("frontend", "enable_button_mode_path"):
        buf = mdutils.text_path2button_path("/%s" % req_path)
        button_path = mdutils.md2html(buf)
    else:
        button_path = None

    full_path = mdutils.req_path_to_full_path(req_path)

    if os.path.isfile(full_path):
        work_full_path = os.path.dirname(full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))

        content = commons.cat(full_path)
        content = commons.strip_bom(content)

        HOME_PAGE = "home"
        if req_path == HOME_PAGE:
            button_path = None
        else:
            enable_show_quick_links = False

    elif os.path.isdir(full_path):
        work_full_path = full_path
        static_file_prefix = os.path.join("/static/pages", req_path)

        content = get_dot_idx_content_by_full_path(full_path) or ""
        if not content:
            content = get_page_file_list_by_req_path(req_path, folder_pages_full_path = folder_pages_full_path)
            if content:
                content = mdutils.sequence_to_unorder_list(content.split("\n"), enable_show_full_path = enable_show_full_path)

    else:
        if req_path == "home" and (not os.path.exists(full_path)):
            return web.seeother("~all")
        else:
            return web.seeother("/%s?action=edit" % req_path)

    content = mdutils.zw_macro2md(text = content,
                                  enable_show_full_path = enable_show_full_path,
                                  folder_pages_full_path = folder_pages_full_path)

    content = mdutils.md2html(text = content,
                              work_full_path = work_full_path,
                              static_file_prefix = static_file_prefix)

    static_files = get_the_same_folders_cssjs_files(req_path)
    if not static_files:
        static_files = static_file.get_global_static_files(enable_auto_toc = enable_auto_toc, enable_highlight = enable_highlight) + "\n"

    try:
        buf = tpl_render.canvas(config = config_agent.config,
                               req_path = req_path,
                               button_path = button_path,
                               content = content,
                               static_files = static_files,
                               enable_show_quick_links = enable_show_quick_links,
                               enable_show_source_button = enable_show_source_button,
                               enable_show_home_link = enable_show_home_link)
    except TypeError, ex:
        msg = "rendering template for '%s' failed. \n" % req_path +\
                "try following command override old templtes files and fix it: \n\n" +\
                "    zwadmin.py upgrade <full path of instance>" + "\n"
        logging.error(msg)

        raise ex

    return buf


def wp_edit(req_path):
    full_path = mdutils.req_path_to_full_path(req_path)

    if config_agent.config.get("frontend", "enable_button_mode_path"):
        buf = mdutils.text_path2button_path("/%s" % req_path)
        title = mdutils.md2html(buf)
    else:
        title = req_path

    create_new = False

    if os.path.isfile(full_path):
        content = commons.cat(full_path)

    elif os.path.isdir(full_path):
        content = get_dot_idx_content_by_full_path(full_path)

    elif not os.path.exists(full_path):
        create_new = True
        content = ""

    else:
        raise Exception("invalid path '%s'" % req_path)

    static_files = static_file.get_global_static_files(enable_auto_toc = False,
                            enable_highlight = False,
                            reader_mode = False)

    return tpl_render.editor(req_path, title, content, create_new = create_new, static_files = static_files)

def wp_rename(req_path):
    full_path = mdutils.req_path_to_full_path(req_path)

    if not os.path.exists(full_path):
        raise web.NotFound()

    return tpl_render.rename(req_path, static_files = static_file.g_global_static_files)

def wp_delete(req_path):
    full_path = mdutils.req_path_to_full_path(req_path)

    delete_page_file_by_full_path(full_path)
    cache.update_recent_change_cache()
    cache.update_all_pages_list_cache()

    web.seeother("/")
    return


def wp_source(req_path):
    full_path = mdutils.req_path_to_full_path(req_path)

    if os.path.isdir(full_path):
        a = os.path.join(full_path, ".index.md")
        b = os.path.join(full_path, ".index.markdown")
        if os.path.exists(a):
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return commons.cat(a)
        elif os.path.exists(b):
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return commons.cat(b)
        else:            
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return "folder doesn't providers source code in Markdown"

    elif os.path.isfile(full_path):
        web.header("Content-Type", "text/plain; charset=UTF-8")
        return commons.cat(full_path)

    else:
        raise web.BadRequest()


def wp_stat():
    stat_tpl = """# Stat

|| _ || _ ||
| Wiki pages | %d |
| Folder | %d |

"""
    folder_page_full_path = config_agent.get_full_path("paths", "pages_path")
    page_count = commons.run(" cd %s ; find . -type f -name '*.md' -or -name '*.markdown' | wc -l " %
                             folder_page_full_path) or 0
    folder_count = commons.run(" cd %s ; find . -type d | wc -l " % folder_page_full_path) or 0
    text = stat_tpl % (int(page_count), int(folder_count))
    content = mdutils.md2html(text)

    return tpl_render.canvas(config = config_agent.config,
                             button_path = None,
                             content = content,
                             req_path = None,
                             static_files = static_file.g_global_static_files,
                             enable_show_quick_links = False)

def wp_new():
    return tpl_render.editor(req_path = "",
                             title = "",
                             content = "",
                             create_new = True,
                             static_files = static_file.g_global_static_files)
