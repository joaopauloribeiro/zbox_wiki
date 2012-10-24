#!/usr/bin/env python
import cgi
import os

import commons
import atom
import cache
import mdutils
import page
import static_file


def generate_feed(config_agent, req_path, tpl_render):
    folder_pages_full_path  = config_agent.config.get("paths", "pages_path")
    cache_file_full_path = os.path.join(folder_pages_full_path, ".zw_all_pages_list_cache")

    buf = cache.get_all_pages_list_from_cache(config_agent)
    md_list = buf.split()

    author = config_agent.config.get("main", "maintainer_email") or "Anonymous"

    e_author = atom.Element(name="author")
    child = atom.Element(name="name", text=author)
    e_author.append_children(child)

    ts = os.stat(cache_file_full_path).st_ctime
    updated = atom.generate_updated(ts)
    ts_as_id = "timestamp:" + commons.strutils.md5(updated)

    feed = atom.Feed(author=e_author, id=ts_as_id, updated=updated, title="Testing Feed Output")
    for md_file_name in md_list[:100]:
        req_path = commons.strutils.rstrips(md_file_name, ".md")
        req_path = commons.strutils.rstrips(req_path, ".markdown")
        local_full_path = mdutils.req_path_to_local_full_path(req_path, folder_pages_full_path)

        raw_text = commons.shutils.cat(local_full_path)
        page_title = mdutils.get_title_by_file_path_in_md(folder_pages_full_path, req_path)

        static_file_prefix = static_file.get_static_file_prefix_by_local_full_path(
            config_agent = config_agent,
            local_full_path = local_full_path,
            req_path = req_path)
        view_settings = page.get_view_settings(config_agent)
        page_content = mdutils.md2html(config_agent = config_agent,
                                  req_path = req_path,
                                  text = raw_text,
                                  static_file_prefix = static_file_prefix,
                                  **view_settings)

        text = cgi.escape(commons.strutils.safestr(page_content))
        e_content = atom.Element(name="content", text=text, type="html")
        if not page_title:
            continue

        hash_title_as_id = "md5:" + commons.strutils.md5(page_title)
        updated = atom.generate_updated(os.stat(local_full_path).st_ctime)
        entry = atom.Entry(id=hash_title_as_id,
                           title=page_title,
                           updated=updated,
                           content=e_content)
        feed.append_children(entry)

    buf = str(feed)
    return buf
