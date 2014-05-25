import os
from zbox_wiki_api import zbox_wiki

instance_full_path = os.path.join(os.getenv("HOME"), "sandbox/proj/man/")

config_agent = zbox_wiki.config_agent
config_full_path = os.path.join(instance_full_path, "/default.cfg")
config = config_agent.load_config([config_full_path], instance_full_path = instance_full_path)
zbox_wiki.config_agent.config = config


folder_pages_full_path = config_agent.config.get("paths", "pages_path")

req_path = "~all"
print zbox_wiki.shell.get_page_file_list_by_req_path(folder_pages_full_path, req_path)

req_path = "."
print zbox_wiki.shell.get_page_file_list_by_req_path(folder_pages_full_path,
                                                     req_path)

req_path = "sa/"
print zbox_wiki.shell.get_page_file_list_by_req_path(folder_pages_full_path,
                                                     req_path)
