import os
import time

import page
import config_agent
import mdutils
import paginator
import static_file
import web


config = config_agent.config

folder_template_full_path = config_agent.get_full_path("paths", "templates_path")
tpl_render = web.template.render(folder_template_full_path)


def update_recent_change_cache():
    buf = page.get_page_file_list_by_req_path(req_path = "~recent",
                                                   sort_by_modified_ts = True)
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_recent_changes_cache")
    file(path, "w").write(buf)

def get_recent_changes_from_cache():
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_recent_changes_cache")

    if os.path.exists(path):
        stat = os.stat(path)

        if (time.time() - stat.st_mtime) > config.getint("cache", "cache_update_interval"):
            update_recent_change_cache()

    else:
        update_recent_change_cache()

    buf = file(path).read()
    return web.utils.safeunicode(buf)


def wp_get_recent_changes_from_cache(enable_show_full_path, limit, offset):
    buf = get_recent_changes_from_cache()
    all_lines = buf.split()
    total_lines = len(all_lines)

    title = "Recent Changes (%d/%d)" % (offset, total_lines / limit)

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
    pg.url = "/~recent"

    return tpl_render.canvas(config = config_agent.config,
                             button_path = title,
                             content = content,
                             static_files = static_file.g_global_static_files,
                             paginator = pg)


def update_all_pages_list_cache():
    buf = page.get_page_file_list_by_req_path(req_path = "~all")
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_all_pages_list_cache")
    file(path, "w").write(buf)

def get_all_pages_list_from_cache():
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_all_pages_list_cache")

    if os.path.exists(path):
        stat = os.stat(path)

        if (time.time() - stat.st_mtime) > config.getint("cache", "cache_update_interval"):
            update_all_pages_list_cache()

    else:
        update_all_pages_list_cache()

    buf = file(path).read()
    return web.utils.safeunicode(buf)
