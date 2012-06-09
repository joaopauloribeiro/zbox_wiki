import os

import config_agent


def append_static_file(text, file_path, file_type, add_newline=False):
    assert file_type in ("css", "js")

    if file_type == "css":
        ref = '<link href="%s" rel="stylesheet" type="text/css">' % file_path
    else:
        ref = '<script type="text/javascript" src="%s"></script>' % file_path

    if not add_newline:
        static_files = "%s\n    %s" % (text, ref)
    else:
        static_files = "%s\n\n    %s" % (text, ref)

    return static_files

def get_global_static_files(enable_auto_toc = None,
                            enable_highlight = None,
                            reader_mode = None):
    if not enable_auto_toc:
        enable_auto_toc = config_agent.config.getboolean("frontend", "enable_auto_toc")
    if not enable_highlight:
        enable_highlight = config_agent.config.getboolean("frontend", "enable_highlight")
    if not reader_mode:
        reader_mode = config_agent.config.getboolean("frontend", "enable_reader_mode")

    static_files = ""

    css_files = ("zw-base.css",)
    for i in css_files:
        path = os.path.join("/static", "css", i)
        static_files = append_static_file(static_files, path, file_type = "css")

    if reader_mode:
        path = os.path.join("/static", "css", "zw-reader.css")
        static_files = append_static_file(static_files, path, file_type = "css")

    if enable_auto_toc:
        path = os.path.join("/static", "css", "zw-toc.css")
        static_files = append_static_file(static_files, path, file_type = "css")


    if enable_highlight:
        path = os.path.join("/static", "js", "prettify", "prettify.css")
        static_files = append_static_file(static_files, path, file_type = "css", add_newline = True)


    static_files = "%s\n" % static_files

    js_files = ("jquery.js", "jquery-ui.js")
    static_files += "\n"
    for i in js_files:
        path = os.path.join("/static", "js", i)
        static_files = append_static_file(static_files, path, file_type = "js")

    js_files = ("zw-base.js", )
    static_files += "\n"
    for i in js_files:
        path = os.path.join("/static", "js", i)
        static_files = append_static_file(static_files, path, file_type = "js")


    if enable_auto_toc:
        static_files += "\n"
        path = os.path.join("/static", "js", "zw-toc.js")
        static_files = append_static_file(static_files, path, file_type = "js")

    if enable_highlight:
        static_files += "\n"
        js_files = (os.path.join("prettify", "prettify.js"), "highlight.js")
        for i in js_files:
            path = os.path.join("/static", "js", i)
            static_files = append_static_file(static_files, path, file_type = "js")

    return static_files
g_global_static_files = get_global_static_files()