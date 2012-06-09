import os
import sys

PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)

if parent_path not in sys.path:
    sys.path.insert(0, parent_path)


from zbox_wiki import paginator