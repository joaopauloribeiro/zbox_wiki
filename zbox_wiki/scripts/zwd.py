#!/usr/bin/env python
import os
from zbox_wiki.commons import argparse
import sys


parser = argparse.ArgumentParser(description = "run ZBox Wiki instance")
parser.add_argument("--ip", help = "the IP address to bind to")
parser.add_argument("--port", type = int, help = "the port number to bind to")
parser.add_argument("--path", help = "instance full path")


def check_conf_compatible_issues(sys_conf, instance_conf, proj_root_full_path):
    changes = ""
    ignore_fields = ("maintainer_email_suffix", "maintainer_email_prefix")

    for key, val in sys_conf.__dict__.iteritems():
        if key in ignore_fields:
            continue

        if key not in instance_conf.__dict__:
            if isinstance(val, basestring):
                changes += key + " = '" + str(val) + "' \n"
            elif isinstance(val, (int, long)):
                changes += key + " = " + str(val) + "\n"

    if changes:
        msg = "\n" \
              "Your instance's configuration file does not compatible with default's, \n" \
              "you have to upgrade your instance: \n\n" \
              "    zwadmin.py upgrade %s \n" % proj_root_full_path
        print msg

        exit( -1 )


def run_instance():
    args = parser.parse_args()

    if not args.path:
        parser.print_help()
        exit(0)

    proj_root_full_path = os.path.realpath(args.path)
    port = args.port or 8080
    ip = args.ip or "0.0.0.0"

    # custom web.py listen IP address and port
    # http://jarln.net/archives/972
    script_name = sys.argv[0]
    listen_ip_port = "%s:%d" % (ip, port)
    fake_argv = [script_name, listen_ip_port]
    sys.argv = fake_argv


    # override zbox_wiki.conf and zbox_wiki.default_conf
    for i in sys.modules.keys():
        if i.startswith("zbox_wiki"):
            del sys.modules[i]

    sys.path.insert(0, proj_root_full_path)
    import conf

    if hasattr(conf, "error_log_path") and conf.error_log_path:
        path = os.path.dirname(conf.error_log_path)
        if not os.path.exists(path):
            os.makedirs(path)

        sys.stderr = file(conf.error_log_path, "a")


    import zbox_wiki
    from zbox_wiki import default_conf

    check_conf_compatible_issues(sys_conf = default_conf,
                                 instance_conf = conf,
                                 proj_root_full_path = proj_root_full_path)

    zbox_wiki.fix_pages_path_symlink(proj_root_full_path)

    os.chdir(conf.pages_path)

    zbox_wiki.srv_start()


if __name__ == "__main__":
    run_instance()
