from __future__ import with_statement

import os
import time

import page
import shell
import web


def update_recent_change_cache(folder_pages_full_path):
    path = os.path.join(folder_pages_full_path, ".zw_recent_changes_cache")
    buf = shell.get_page_file_list_by_req_path(folder_pages_full_path = folder_pages_full_path,
                                              req_path = "~recent", sort_by_modified_ts = True)

    with open(path, "w") as f:
        f.write(buf)

def get_recent_changes_from_cache(config_agent):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_recent_changes_cache")

    if os.path.exists(path):
        stat = os.stat(path)

        if (time.time() - stat.st_mtime) > config_agent.config.getint("cache", "cache_update_interval"):
            update_recent_change_cache(config_agent)
    else:
        update_recent_change_cache(config_agent)

    with open(path) as f:
        buf = f.read()

    return web.utils.safeunicode(buf)

def update_all_pages_list_cache(folder_pages_full_path):
    buf = shell.get_page_file_list_by_req_path(folder_pages_full_path = folder_pages_full_path, req_path = "~all")
    path = os.path.join(folder_pages_full_path, ".zw_all_pages_list_cache")

    with open(path, "w") as f:
        f.write(buf)

def get_all_pages_list_from_cache(config_agent):
    folder_pages_full_path = config_agent.get_full_path("paths", "pages_path")
    path = os.path.join(folder_pages_full_path, ".zw_all_pages_list_cache")

    if os.path.exists(path):
        stat = os.stat(path)

        if (time.time() - stat.st_mtime) > config_agent.config.getint("cache", "cache_update_interval"):
            update_all_pages_list_cache(folder_pages_full_path)
    else:
        update_all_pages_list_cache(folder_pages_full_path)

    with open(path) as f:
        buf = f.read()

    return web.utils.safeunicode(buf)
