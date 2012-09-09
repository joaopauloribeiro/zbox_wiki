#!/usr/bin/env python
import os
import re
import commons


def match_in_re(name, patterns):
    for p in patterns:
        re_obj = re.compile(p)
        if re_obj.match(name):
            return True

    return False

def get_files_list(path, ignore_patterns = ['^\.(.+?)$', '^(.+?)~$'], match_patterns = None):
    """ `ignore_patterns` is a list of regular expressions, ignore '.DS_Store', 'foo~' etc by default. """
    files = []
    for pending_filename in os.listdir(path):
        if ignore_patterns:
            if match_in_re(name = pending_filename, patterns = ignore_patterns):
                continue
        if match_patterns:
            if not match_in_re(name = pending_filename, patterns = match_patterns):
                continue
        files.append(pending_filename)
    return files


def fix_pattern(p):
    try:
        re.compile(p)
    except:
        if p.startswith("*.") and p.count("*.") == 1:
            suffix = p.split("*.")[-1]
            fixed = "^(.+?)\.%s$" % suffix
            return fixed
        else:
            print "expected regular expression or '*.suffix' style expression, got `%s`" % p
            return None

    return p

def parse_work_path(path, folder_pages_full_path):
    if os.path.exists(path):
        return path
    elif path.startswith("/"):
        par = os.path.dirname(path)
        if os.path.exists(par):
            return par

    if folder_pages_full_path is not None:
        full_path = os.path.join(folder_pages_full_path, path)
        if os.path.exists(full_path):
            return full_path

        par = os.path.dirname(full_path)
        if os.path.exists(par):
            return par

    return path

def cat_files(work_path, files):
    buf = ""
    for filename in files:
        full_path = os.path.join(work_path, filename)
        chunk = "%s" % filename
        chunk += "\n"
        with open(full_path) as f:
            chunk += f.read()
        chunk += "\n"
        buf += chunk

    return buf


def macro_zw2md_cat(text, folder_pages_full_path = None, **view_settings):
    shebang_p = "#!zw"
    code_p = '(?P<code>[^\f\v]+?)'
    code_block_p = "^\{\{\{[\s]*%s*%s[\s]*\}\}\}" % (shebang_p, code_p)
    p_obj = re.compile(code_block_p, re.MULTILINE)

    def code_repl(match_obj):
        code = match_obj.group('code')
        code = code.split("\n")[1]

        if code.startswith("cat("):
            p = 'cat\("(?P<path>.+?)"\)'
            m = re.match(p, code, re.UNICODE | re.MULTILINE)
            path = m.group("path")
            path = commons.strutils.strips(path, "\n")

            work_path = parse_work_path(path, folder_pages_full_path)

            match_pattern = commons.strutils.lstrips(path, work_path)
            match_pattern = commons.strutils.strips(match_pattern, "/")
            match_pattern = fix_pattern(match_pattern)

            print "work_path = ", work_path
            print "match_pattern = ", match_pattern

            files = get_files_list(path = work_path, match_patterns = [match_pattern])

            print "files = ", files

            buf = cat_files(work_path = work_path, files = files)
            return buf

#        return code
        buf_fixed = "{{{#!zw\n%s\n}}}" % code
        return buf_fixed

    return p_obj.sub(code_repl, text)

def test_fix_pattern():
    auto_patterns = (
        ("*.md", "^(.+?)\.md$"),
        ("^(.+?)\.md$", "^(.+?)\.md$"),
    )

    for e, g in auto_patterns:
        assert fix_pattern(e) == g


def test_macro_cat():
    text = """
{{{#!zw
cat("/Users/lee/lees_wiki/pages/*.md")
}}}
"""

    result = macro_zw2md_cat(text)
    result = commons.strutils.strips(result, "\n")
    print repr(result)


if __name__ == "__main__":
    test_fix_pattern()
    test_macro_cat()
