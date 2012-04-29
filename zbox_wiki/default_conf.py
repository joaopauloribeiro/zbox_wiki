import os
PWD = os.path.dirname(os.path.realpath(__file__))


version = 201204
debug = True

readonly = 1

#error_log_path = os.path.join(PWD, "tmp", "error_log.txt")
error_log_path = None

maintainer_email = "shuge.lee@gmail.com"
repository_url = "git://github.com/shuge/zbox_wiki.git"


# paths
pages_path = os.path.join(PWD, "pages")

static_path = os.path.join(PWD, "static")
sessions_path = os.path.join(PWD, 'sessions')
tmp_path = os.path.join(PWD, "tmp")
templates_path = os.path.join(PWD, "templates")


# cache, default 1 minute
cache_update_interval = 60


# pagination
page_limit = 50
search_page_limit = 100


# html render
show_full_path = 0
auto_toc = 1
highlight = 1

show_quick_links = 1
show_home_link = 1
home_link_name = "Home"

button_mode_path = 1
reader_mode = 1
show_source_button = 1


if maintainer_email:
    splits = maintainer_email.split("@")
    maintainer_email_prefix = splits[0]
    maintainer_email_suffix = splits[1]
