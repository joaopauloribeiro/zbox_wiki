#!/usr/bin/env python
import os
import sys
import web

PWD = os.path.dirname(os.path.realpath(__file__))
parent_path = os.path.dirname(PWD)
if parent_path not in sys.path:
    sys.path.insert(0, parent_path)


print 'asdf'