import logging
import os
import web

import cache
import commons
import mdutils
import paginator
import static_file


logging.getLogger("page").setLevel(logging.DEBUG)


def get_dot_idx_content_by_full_path(full_path):
    dot_idx_full_path = os.path.join(full_path, "index.md")
    return commons.shutils.cat(dot_idx_full_path)


def get_page_file_list_by_req_path(folder_pages_full_path, req_path, sort_by_modified_ts = False, max_depth = None, limit = None):
    if req_path in ("~all", "~recent"):
        path = "."
    else:
        path = web.utils.strips(req_path, "/")

    if max_depth is None:
        cmd = " cd %s; find %s -follow -name '*.md' -or -name '*.markdown'  " % \
            (folder_pages_full_path, path)
    else:
        cmd = " cd %s; find %s -maxdepth %d -follow -name '*.md' -or -name '*.markdown'  " % \
            (folder_pages_full_path, path, max_depth)
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
        idx_dot_md = os.path.join(full_path, "index.md")
        os.remove(idx_dot_md)
        return True
    return False

def get_the_same_folders_cssjs_files(req_path, local_full_path, folder_pages_full_path):
    """ NOTICE: this features doesn't works on some file systems, such as those mounted by sshfs """
    if os.path.isfile(local_full_path):
        work_path = os.path.dirname(local_full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))

    elif os.path.isdir(local_full_path):
        work_path = local_full_path
        static_file_prefix = os.path.join("/static/pages", req_path)

    elif req_path == "home":
        work_path = os.path.dirname(local_full_path)
        static_file_prefix = os.path.join("/static/pages", os.path.dirname(req_path))

    else:
        # special pages, such as '/~all'
        work_path = folder_pages_full_path
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
    full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    if full_path.endswith((".md", ".markdown")):
        folder_parent = os.path.dirname(full_path)
        if not os.path.exists(folder_parent):
            os.makedirs(folder_parent)

    if not os.path.isdir(full_path):
        web.utils.safewrite(full_path, content.replace("\r\n", "\n"))
    else:
        idx_dot_md_full_path = os.path.join(full_path, "index.md")
        web.utils.safewrite(idx_dot_md_full_path, content.replace("\r\n", "\n"))


def wp_read(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    HOME_PAGE = ""
    if req_path != HOME_PAGE and view_settings["button_mode_path"]:
        buf = mdutils.text_path_to_button_path("/%s" % req_path)
        button_path = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = buf)
    else:
        button_path = None
        view_settings["show_quick_links"] = False

    if os.path.isfile(local_full_path):
        content = commons.shutils.cat(local_full_path)
        content = commons.strutils.strip_bom(content)

    elif os.path.isdir(local_full_path):
        # try /path/to/folder/index
        content = get_dot_idx_content_by_full_path(local_full_path) or ""
        if not content:
            # try /path/to/folder/*
            content = get_page_file_list_by_req_path(folder_pages_full_path = folder_pages_full_path, req_path = req_path)
            if content:
                content = mdutils.sequence_to_unorder_list(content.split("\n"), **view_settings)
    else:
        # /index does not exists
        if req_path == HOME_PAGE:
            return web.seeother("~all")
        else:
            return web.seeother("/%s?action=edit" % req_path)

    title = mdutils.get_title_from_md(full_path = local_full_path)
    content = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = content)

    static_files = get_the_same_folders_cssjs_files(req_path = req_path, local_full_path = local_full_path,
                                                    folder_pages_full_path = folder_pages_full_path)
    if not static_files:
        static_files = static_file.get_global_static_files(**view_settings) + "\n"

    buf = tpl_render.canvas(config = config_agent.config,
                            static_files = static_files,
                            button_path = button_path,
                            req_path = req_path,
                            title = title,
                            content = content,
                            **view_settings)
#    try:
#        buf = tpl_render.canvas(config = config_agent.config,
#                                static_files = static_files, button_path = button_path, content = content,
#                                **view_settings)
#    except TypeError, ex:
#        logging.error(str(ex))
#        buf = "Rendering template for '%s' failed. \n" % req_path +\
#                "try following command override old templtes files and fix it: \n\n" +\
#                "    zwadmin.py upgrade <full path of instance>" + "\n"
#        logging.error(buf)

    return buf


def wp_edit(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)

    view_settings["auto_toc"] = False
    view_settings["highlight_code"] = False
    view_settings["reader_mode"] = False
    static_files = static_file.get_global_static_files(**view_settings)

    full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    if config_agent.config.get("frontend", "button_mode_path"):
        buf = mdutils.text_path_to_button_path("/%s" % req_path)
        title = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = buf, **view_settings)
    else:
        title = req_path

    create_new = False

    if os.path.isfile(full_path):
        content = commons.shutils.cat(full_path)

    elif os.path.isdir(full_path):
        content = get_dot_idx_content_by_full_path(full_path)

    elif not os.path.exists(full_path):
        create_new = True
        content = ""

    else:
        raise Exception("invalid path '%s'" % req_path)

    return tpl_render.editor(config_agent = config_agent,
                             static_files = static_files,
                             req_path = req_path,
                             create_new = create_new,
                             title = title,
                             content = content,
                             **view_settings)

def wp_rename(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**view_settings)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path = req_path,
                                                          folder_pages_full_path = folder_pages_full_path)
    if not os.path.exists(local_full_path):
        raise web.NotFound()

    title = "Rename %s" % req_path
    old_path = req_path

    return tpl_render.rename(config_agent = config_agent,
                             static_files = static_files,
                             title = title,
                             old_path = old_path,
                             **view_settings)

def wp_delete(config_agent, tpl_render, req_path):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    delete_page_file_by_full_path(local_full_path)
    cache.update_recent_change_cache(config_agent)
    cache.update_all_pages_list_cache(config_agent)

    web.seeother("/")
    return


def wp_source(config_agent, tpl_render, req_path):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    if os.path.isdir(local_full_path):
        a = os.path.join(local_full_path, "index.md")
        b = os.path.join(local_full_path, "index.markdown")

        if os.path.exists(a):
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return commons.shutils.cat(a)

        elif os.path.exists(b):
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return commons.shutils.cat(b)

        else:            
            web.header("Content-Type", "text/plain; charset=UTF-8")
            return "folder doesn't providers source code in Markdown"

    elif os.path.isfile(local_full_path):
        web.header("Content-Type", "text/plain; charset=UTF-8")
        return commons.shutils.cat(local_full_path)

    raise web.NotFound()


def wp_stat(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)
    view_settings["show_quick_links"] = False
    view_settings["show_toolbox"] = False
    static_files = static_file.get_global_static_files(**view_settings)

    title = "Stat"

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
    content = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = text)

    return tpl_render.canvas(config = config_agent.config,
                             static_files = static_files,
                             button_path = None,
                             req_path = req_path,
                             title = title,
                             content = content,
                             **view_settings)

def wp_new(config_agent, req_path, tpl_render):
    view_settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**view_settings)

    title = "Create %s" % req_path

    return tpl_render.editor(config_agent = config_agent,
                             static_files = static_files,
                             req_path = req_path,
                             title = title,
                             content = "",
                             create_new = True,
                             **view_settings)


def get_view_settings(config_agent):
    theme_name = config_agent.config.get("frontend", "theme_name")

    c_fp = config_agent.config.get("frontend", "show_full_path")
    show_full_path = int(web.cookies().get("zw_show_full_path", c_fp))

    c_toc = config_agent.config.getboolean("frontend", "auto_toc")
    auto_toc = int(web.cookies().get("zw_auto_toc", c_toc))

    c_hc = config_agent.config.get("frontend", "highlight_code")
    highlight_code = int(web.cookies().get("zw_highlight", c_hc))

    reader_mode = config_agent.config.getboolean("frontend", "reader_mode")

    show_quick_links = config_agent.config.getboolean("frontend", "show_quick_links")
    show_home_link = config_agent.config.getboolean("frontend", "show_home_link")

    button_mode_path = config_agent.config.getboolean("frontend", "button_mode_path")
    show_toolbox = True
    show_view_source_button = config_agent.config.getboolean("frontend", "show_view_source_button")

    settings = dict(theme_name = theme_name,
                    show_full_path = show_full_path,
                    auto_toc = auto_toc, highlight_code = highlight_code, reader_mode = reader_mode,
                    show_quick_links = show_quick_links, show_home_link = show_home_link,
                    button_mode_path = button_mode_path,
                    show_toolbox = show_toolbox,
                    show_view_source_button = show_view_source_button)
    return settings


def wp_view_settings(config_agent, tpl_render):
    settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**settings)
    return tpl_render.view_settings(static_files = static_files, **settings)


def wp_get_all_pages(config_agent, tpl_render, req_path, limit, offset):
    view_settings = get_view_settings(config_agent)
    view_settings["show_toolbox"] = False

    buf = cache.get_all_pages_list_from_cache(config_agent)
    all_lines = buf.split()
    total_lines = len(all_lines)
    title = "All Pages List (%d/%d)" % (offset, total_lines / limit)

    start = offset * limit
    end = start + limit
    lines = all_lines[start:end]

    buf = mdutils.sequence_to_unorder_list(lines, **view_settings)
    content = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = buf, **view_settings)

    static_files = static_file.get_global_static_files(**view_settings)

    pg = paginator.Paginator()
    pg.total = total_lines
    pg.current_offset = offset
    pg.limit = limit
    pg.url = "/~all"

    return tpl_render.canvas(config = config_agent.config,
                             static_files = static_files,
                             button_path = title,
                             req_path = "~all",
                             title = title,
                             content = content,
                             paginator = pg,
                             **view_settings)

def wp_get_recent_changes_from_cache(config_agent, tpl_render, req_path, limit, offset):
    view_settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**view_settings)

    buf = cache.get_recent_changes_from_cache(config_agent)
    all_lines = buf.split()
    total_lines = len(all_lines)

    title = "Recent Changes (%d/%d)" % (offset, total_lines / limit)

    start = offset * limit
    end = start + limit
    lines = all_lines[start : end]

    buf = mdutils.sequence_to_unorder_list(lines, **view_settings)
    content = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = buf, **view_settings)

    pg = paginator.Paginator()
    pg.total = total_lines
    pg.current_offset = offset
    pg.limit = limit
    pg.url = "/~recent"

    return tpl_render.canvas(config = config_agent.config,
                             static_files = static_files,
                             button_path = title,
                             req_path = req_path,
                             title = title,
                             content = content,
                             paginator = pg,
                             **view_settings)
