#!/usr/bin/env python
import os
import sys

from commons import argparse


default_port = 8080
default_addr = "0.0.0.0"

parser = argparse.ArgumentParser(description = "run ZBox Wiki instance", epilog = "Please report bug to shuge.lee <AT> GMail.")
parser.add_argument("--ip", help = "the IP address to bind to")
parser.add_argument("--port", type = int, help = "the port number to bind to")
parser.add_argument("--path", help = "full path of instance")


def check_conf_compatible_issues(sys_conf, instance_conf, instance_root_full_path):
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
              "    zwadmin.py upgrade %s \n" % instance_root_full_path
        print msg

        exit( -1 )

def run_instance(args):
    instance_root_full_path = os.path.realpath(args.path)
    port = args.port or default_port
    ip = args.ip or default_addr

    # custom web.py listen IP address and port
    # http://jarln.net/archives/972
    script_name = sys.argv[0]
    listen_ip_port = "%s:%d" % (ip, port)
    fake_argv = [script_name, listen_ip_port]
    sys.argv = fake_argv


    from zbox_wiki import config_agent
    instance_config_file_full_path = os.path.join(instance_root_full_path, "default.cfg")
    instance_config = config_agent.load_config(paths = [instance_config_file_full_path],
                                               instance_full_path = instance_root_full_path)
    config_agent.config = instance_config

    pages_path = config_agent.get_full_path("paths", "pages_path")
    os.chdir(pages_path)

    import zbox_wiki
    zbox_wiki.main(instance_root_full_path)


if __name__ == "__main__":
    args = parser.parse_args()

    if args.path:
        run_instance(args)
        exit(0)

    parser.print_help()

