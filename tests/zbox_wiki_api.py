import os
import sys

PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

if parent_path not in sys.path:
    sys.path.insert(0, parent_path)

import zbox_wiki


web_url = 'http://0.0.0.0:8000/'
instance_url = "/tmp/hello"