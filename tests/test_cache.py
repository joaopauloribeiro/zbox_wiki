#!/usr/bin/env python
import os
import api

config_agent = api.zbox_wiki.config_agent
config_path = os.path.join(api.instance_full_path, "/default.cfg")
config = config_agent.load_config([config_path], instance_full_path = api.instance_full_path)
api.zbox_wiki.config_agent.config = config

#print config_agent.config.get("paths", "instance_full_path")
#print config_agent.get_full_path("paths", "pages_path")

print api.zbox_wiki.cache.get_all_pages_list_from_cache(config_agent)