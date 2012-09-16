import logging
import os
import shutil

import web

import cache
import consts
import commons
import mdutils
import paginator
import search
import shell
import static_file


logging.getLogger("page").setLevel(logging.DEBUG)


def delete_page_file_by_full_path(local_full_path):
    if os.path.isfile(local_full_path):
        os.remove(local_full_path)
        return True
    elif os.path.isdir(local_full_path):
        idx_dot_md = os.path.join(local_full_path, "index.md")
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

def wp_create(config_agent, req_path, path, content):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(path, folder_pages_full_path)

    if path.endswith("/"):
        file_full_path = os.path.join(local_full_path, "index.md")
    else:
        file_full_path = local_full_path

    parent_path = os.path.dirname(file_full_path)
    if not os.path.exists(parent_path):
        os.makedirs(parent_path)

    with open(file_full_path, "w'") as f:
        f.write(content)

    cache.update_recent_change_cache(folder_pages_full_path)
    cache.update_all_pages_list_cache(folder_pages_full_path = folder_pages_full_path)

    web.seeother(path)


def wp_read(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)
    static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(config_agent = config_agent,
                                                                               local_full_path = local_full_path,
                                                                               req_path = req_path)
    path_info = web.ctx.environ["PATH_INFO"]

    HOME_PAGE = ""
    if req_path != HOME_PAGE and view_settings["button_mode_path"]:
        buf = mdutils.text_path_to_button_path("/%s" % req_path)
        button_path = mdutils.md2html(config_agent = config_agent, req_path = req_path, text = buf,
                                      static_file_prefix = static_file_prefix, **view_settings)
    else:
        button_path = None
        view_settings["show_quick_links"] = False

    if os.path.isfile(local_full_path):
        # os.path.exists(local_full_path)
        buf = commons.shutils.cat(local_full_path)
        buf = commons.strutils.strip_bom(buf)

    elif os.path.isdir(local_full_path):
        # os.path.exists(local_full_path)
        if req_path == HOME_PAGE:
            a = os.path.join(local_full_path, "index.md")
            b = os.path.join(local_full_path, "index.markdown")
            if os.path.exists(a) or os.path.exists(b):
                fixed_req_path = os.path.join(path_info, "index")
                return web.seeother(fixed_req_path)
            else:
                fixed_req_path = os.path.join(path_info, "~all")
                return web.seeother(fixed_req_path)
        else:
            # listdir /path/to/folder/*
            buf = shell.get_page_file_list_by_req_path(folder_pages_full_path = folder_pages_full_path, req_path = req_path)
            if buf:
                buf = mdutils.sequence_to_unorder_list(buf.split("\n"), **view_settings)
            else:
                buf = "folder `%s` exists, but there is no files" % path_info
    else:
        # not os.path.exists(local_full_path)
        if path_info.endswith("/"):
            fixed_req_path = path_info + "index?action=update"
        else:
            fixed_req_path = path_info + "?action=update"
        return web.seeother(fixed_req_path)

    title = mdutils.get_title_from_md(local_full_path = local_full_path)
    content = mdutils.md2html(config_agent = config_agent,
                              req_path = req_path,
                              text = buf,
                              static_file_prefix = static_file_prefix,
                              **view_settings)

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

    return buf


def wp_update(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent, simple = True)
    static_files = static_file.get_global_static_files(**view_settings)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    title = "Editing %s" % req_path
    create_new = False

    if local_full_path.endswith("/"):
        msg = "not allow to edit path/to/folder, using path/to/folder/index instead"
        raise web.BadRequest(message = msg)

    # os.path.exists(local_full_path)
    if os.path.isfile(local_full_path):
        buf = commons.shutils.cat(local_full_path)
    else:
        # not os.path.exists(local_full_path)
        create_new = True
        buf = ""

    return tpl_render.update(config_agent = config_agent,
                             static_files = static_files,
                             req_path = req_path,
                             create_new = create_new,
                             title = title,
                             content = buf,
                             **view_settings)

def wp_update_post(config_agent, req_path, new_content):
    path_info = web.ctx.environ["PATH_INFO"]

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    folder_parent = os.path.dirname(local_full_path)
    if not os.path.exists(folder_parent):
        os.makedirs(folder_parent)

    content = new_content.replace("\r\n", "\n")

    with open(local_full_path, "w") as f:
        f.write(content)

    cache.update_recent_change_cache(folder_pages_full_path)

    return web.seeother(path_info)


def wp_rename(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent, simple = True)
    static_files = static_file.get_global_static_files(**view_settings)

    title = "Rename %s" % req_path
    old_path = req_path

    return tpl_render.rename(config_agent = config_agent,
                             static_files = static_files,
                             title = title,
                             old_path = old_path,
                             **view_settings)

def wp_rename_post(config_agent, tpl_render, req_path, new_path):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")

    old_path = req_path
    old_full_path = mdutils.req_path_to_local_full_path(old_path, folder_pages_full_path)
    new_full_path = mdutils.req_path_to_local_full_path(new_path, folder_pages_full_path)

    if old_full_path == new_full_path:
        return web.seeother("/%s" % new_path)
    elif not os.path.exists(old_full_path):
        msg = "old %s doesn't exists" % old_full_path
        raise web.BadRequest(msg)

    msg = """<pre>
allow
    file -> new_file
    folder -> new_folder

not allow
    file -> new_folder
    folder -> new_file
</pre>"""

    if os.path.isfile(old_full_path):
        if new_full_path.endswith("/"):
            raise web.BadRequest(msg)
    elif os.path.isdir(old_full_path):
        if not new_full_path.endswith("/"):
            raise web.BadRequest(msg)

    parent = os.path.dirname(new_full_path)
    if not os.path.exists(parent):
        os.makedirs(parent)

    shutil.move(old_full_path, new_full_path)

    cache.update_all_pages_list_cache(folder_pages_full_path)
    cache.update_recent_change_cache(folder_pages_full_path)

    if os.path.isfile(new_full_path):
        return web.seeother("/%s" % new_path)
    elif os.path.isdir(new_full_path):
        return web.seeother("/%s/" % new_path)
    else:
        raise web.BadRequest()

def wp_delete(config_agent, tpl_render, req_path):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    if os.path.isfile(local_full_path):
        redirect_to = os.path.dirname(local_full_path)
        delete_page_file_by_full_path(local_full_path)
    elif os.path.isdir(local_full_path):
        buf = commons.strutils.rstrip(local_full_path, "/")
        redirect_to = os.path.dirname(buf)
        delete_page_file_by_full_path(local_full_path)
    else:
        raise web.NotFound()

    cache.update_recent_change_cache(folder_pages_full_path)
    cache.update_all_pages_list_cache(folder_pages_full_path)

    return web.seeother(redirect_to)


def wp_source(config_agent, tpl_render, req_path):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

    if os.path.isfile(local_full_path):
        web.header("Content-Type", "text/plain; charset=UTF-8")
        buf = commons.shutils.cat(local_full_path)
        return buf
    elif os.path.isdir(local_full_path):
        msg = "folder doesn't providers source in Markdown, using file instead"
        raise web.BadRequest(msg)
    else:
        raise web.NotFound()

_stat_tpl = """# Stat

|| _ || _ ||
| Wiki pages | %d |
| Folder | %d |

"""

def wp_stat(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)
    view_settings["show_quick_links"] = False
    view_settings["show_toolbox"] = False

    static_files = static_file.get_global_static_files(**view_settings)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path = req_path, folder_pages_full_path = folder_pages_full_path)
    static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(config_agent = config_agent,
                                                                               local_full_path = local_full_path,
                                                                               req_path = req_path)
    title = "Stat"

    page_count = commons.shutils.run(" cd %s ; find . -type f -name '*.md' -or -name '*.markdown' | wc -l " %
                             folder_pages_full_path) or 0
    folder_count = commons.shutils.run(" cd %s ; find . -type d | wc -l " % folder_pages_full_path) or 0
    buf = _stat_tpl % (int(page_count), int(folder_count))
    content = mdutils.md2html(config_agent = config_agent,
                              req_path = req_path,
                              text = buf,
                              static_file_prefix = static_file_prefix,
                              **view_settings)

    return tpl_render.canvas(config = config_agent.config,
                             static_files = static_files,
                             button_path = "",
                             req_path = req_path,
                             title = title,
                             content = content,
                             **view_settings)

def wp_new(config_agent, req_path, tpl_render):
    view_settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**view_settings)

    title = "Create %s" % req_path

    return tpl_render.update(config_agent = config_agent,
                             static_files = static_files,
                             req_path = "",
                             title = title,
                             content = "",
                             create_new = True,
                             **view_settings)


def get_view_settings(config_agent, simple = False):
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

    if simple:
        auto_toc = False
        reader_mode = False
        highlight_code = False

    settings = dict(theme_name = theme_name,
                    show_full_path = show_full_path,
                    auto_toc = auto_toc, highlight_code = highlight_code, reader_mode = reader_mode,
                    show_quick_links = show_quick_links, show_home_link = show_home_link,
                    button_mode_path = button_mode_path,
                    show_toolbox = show_toolbox,
                    show_view_source_button = show_view_source_button)
    return settings


def wp_view_settings(config_agent, tpl_render, req_path):
    settings = get_view_settings(config_agent)
    static_files = static_file.get_global_static_files(**settings)
    return tpl_render.view_settings(static_files = static_files, **settings)


def wp_get_all_pages(config_agent, tpl_render, req_path, limit, offset):
    view_settings = get_view_settings(config_agent)
    view_settings["show_toolbox"] = False

    static_files = static_file.get_global_static_files(**view_settings)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)
    static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(config_agent = config_agent,
                                                                                local_full_path = local_full_path,
                                                                                req_path = req_path)

    buf = cache.get_all_pages_list_from_cache(config_agent)
    all_lines = buf.split()
    total_lines = len(all_lines)
    title = "All Pages List (%d/%d)" % (offset, total_lines / limit)

    start = offset * limit
    end = start + limit
    lines = all_lines[start:end]

    buf = mdutils.sequence_to_unorder_list(lines, **view_settings)
    content = mdutils.md2html(config_agent = config_agent,
                              req_path = req_path, text = buf,
                              static_file_prefix = static_file_prefix,
                              **view_settings)

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

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path,
                                                          folder_pages_full_path)
    static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(
        config_agent = config_agent,
        local_full_path = local_full_path,
        req_path = req_path)

    buf = cache.get_recent_changes_from_cache(config_agent)
    all_lines = buf.split()
    total_lines = len(all_lines)

    title = "Recent Changes (%d/%d)" % (offset, total_lines / limit)

    start = offset * limit
    end = start + limit
    lines = all_lines[start : end]

    buf = mdutils.sequence_to_unorder_list(lines, **view_settings)
    content = mdutils.md2html(config_agent = config_agent,
                              req_path = req_path,
                              text = buf,
                              static_file_prefix = static_file_prefix,
                              **view_settings)

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



def wp_search(config_agent, tpl_render, req_path):
    view_settings = get_view_settings(config_agent)

    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    local_full_path = mdutils.req_path_to_local_full_path(req_path,
                                                          folder_pages_full_path)
    static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(
        config_agent = config_agent,
        local_full_path = local_full_path,
        req_path = req_path)

    keywords = web.input().get("k")
    keywords = web.utils.safestr(keywords)
    title = "Search %s" % keywords

    if keywords:
        limit = config_agent.config.getint("pagination", "search_page_limit")
        lines = search.search_by_filename_and_file_content(keywords,
                                                          limit = limit)
        if lines:
            buf = mdutils.sequence_to_unorder_list(seq = lines, **view_settings)
        else:
            buf = None
    else:
        buf = None

    if buf:
        content = mdutils.md2html(config_agent = config_agent,
                                  req_path = req_path,
                                  text = buf,
                                  static_file_prefix = static_file_prefix,
                                  **view_settings)
    else:
       content = "matched not found"

    static_files = static_file.get_global_static_files(**view_settings)

    return tpl_render.search(config_agent = config_agent,
                             static_files = static_files,
                             title = title,
                             keywords = keywords,
                             content = content)