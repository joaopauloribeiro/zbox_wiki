#!/usr/bin/env python
import os
import platform
import shutil
import sys
import logging
import hashlib
import zbox_wiki


logging.getLogger().setLevel(logging.INFO)

md5 = lambda plain : hashlib.md5(plain).hexdigest()


ZW_MOD_FULL_PATH = zbox_wiki.__path__[0]

IS_DEB_BASED = platform.linux_distribution()[0].lower()
if IS_DEB_BASED not in ("ubuntu", "debian"):
    IS_DEB_BASED = None


ZWADMIN_HELP_MSG = """
Usage:

    zwadmin.py create <path>
    zwadmin.py deploy <path>
    zwadmin.py upgrade <path>

Please report bug to shuge.lee <AT> GMail.
"""

ZWD_UBUNTU_HELP_MSG = """
start ZBox Wiki:
    zwd.py --path %s

If you want to run it as daemon/FCGI:

    sudo apt-get install nginx spawn-fcgi python-flup --no-install-recommends

    cd %s

    sudo cp nginx-debian.conf /etc/nginx/sites-available/zboxwiki
    sudo ln -sf /etc/nginx/sites-available/zboxwiki /etc/nginx/sites-enabled/zboxwiki
    sudo /etc/init.d/nginx restart

    sh start_fcgi.sh

Visit
    http://localhost:8080

View its log:

    tail -f /var/log/nginx/error.log

Stop process:

    sh stop_fcgi.sh

Please report bug to shuge.lee <AT> GMail.
"""

ZWD_HELP_MSG = """
start ZBox Wiki:
    zwd.py --path %s

If you want to run it as daemon/FCGI,
visit http://webpy.org/cookbook/fastcgi-nginx for more information.

Please report bug to shuge.lee <AT> GMail.
"""


def print_zwadmin_help_msg():
    sys.stdout.write(ZWADMIN_HELP_MSG)

def print_zwd_help_msg(proj_root_path):
    if IS_DEB_BASED:
        msg = ZWD_UBUNTU_HELP_MSG % (proj_root_path, proj_root_path, proj_root_path)
    else:
        msg = ZWD_HELP_MSG % proj_root_path

    sys.stdout.write(msg)


def cp_fcgi_scripts(proj_root_path):
    src = os.path.join(ZW_MOD_FULL_PATH, "scripts", "fcgi_main.py")
    dst = os.path.join(proj_root_path, "fcgi_main.py")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0774)

    src = os.path.join(ZW_MOD_FULL_PATH, "scripts", "start_fcgi.sh")
    dst = os.path.join(proj_root_path, "start_fcgi.sh")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0774)

    src = os.path.join(ZW_MOD_FULL_PATH, "scripts", "stop_fcgi.sh")
    dst = os.path.join(proj_root_path, "stop_fcgi.sh")
    shutil.copyfile(src, dst)
    os.chmod(dst, 0774)


    if IS_DEB_BASED:
        conf_file_name = "nginx-debian.conf"

        nginx_conf_tpl = os.path.join(proj_root_path, "pages", "zbox-wiki", conf_file_name)
        buf = file(nginx_conf_tpl).read()
        buf = buf.replace("/path/to/zw_instance", proj_root_path)
        nginx_conf_path = os.path.join(proj_root_path, conf_file_name)
        file(nginx_conf_path, "w").write(buf)

def cp_folder_templates(ZW_MOD_FULL_PATH, proj_root_path, confirm = True):
    folder_name = "templates"
    src_prefix = os.path.join(ZW_MOD_FULL_PATH, folder_name)
    dst_prefix = os.path.join(proj_root_path, folder_name)

    for i in os.listdir(src_prefix):
        src = os.path.join(src_prefix, i)
        dst = os.path.join(dst_prefix, i)

        if os.path.exists(dst):
            with open(src, "rb") as f:
                src_text = f.read().strip()

            with open(dst, "rb") as f:
                dst_text = f.read().strip()

            if (md5(src_text) != md5(dst_text)) and confirm:
                ans = raw_input("%s already exists, override it? [y/N]" % dst)
                if ans in ("y", "Y"):
                    os.remove(dst)
                else:
                    continue

        shutil.copy(src, dst)
        logging.info("%s -> %s" % (src, dst))

def action_create(proj_root_path):
    import zbox_wiki
    ZW_MOD_FULL_PATH = zbox_wiki.__path__[0]


    for folder_name in ("static", "templates", "pages"):
        src = os.path.join(ZW_MOD_FULL_PATH, folder_name)
        dst = os.path.join(proj_root_path, folder_name)

        if os.path.exists(dst):
            msg = dst + " already exists, skip \n"
            sys.stdout.write(msg)
            continue
        shutil.copytree(src, dst)


    for folder_name in ("tmp", "sessions"):
        src_full_path = os.path.join(proj_root_path, folder_name)

        if os.path.exists(src_full_path):
            msg = src_full_path + "already exists, skip \n"
            sys.stdout.write(msg)
            continue

        os.mkdir(src_full_path)


    src = os.path.join(ZW_MOD_FULL_PATH, "default_conf.py")
    dst = os.path.join(proj_root_path, "conf.py")
    if os.path.exists(dst):
        msg = dst + " already exists, skip \n"
        sys.stdout.write(msg)
    else:
        shutil.copyfile(src, dst)


    cp_fcgi_scripts(proj_root_path)

    print_zwd_help_msg(proj_root_path)

def append_maintainer_email(maintainer_email):
    tpl = """if maintainer_email:
    splits = maintainer_email.split("@")
    maintainer_email_prefix = splits[0]
    maintainer_email_suffix = splits[1]

"""
    if maintainer_email:
        return tpl
    else:
        return ""

def action_upgrace(proj_root_path):    
    upgrade_config_file(proj_root_path)
    upgrade_template_files(proj_root_path)

    instance_conf_full_path = os.path.join(proj_root_path, "conf.py")
    default_conf_full_path = os.path.join(ZW_MOD_FULL_PATH, "default_conf.py")
    
    msg = """
Upgrading done.

If it does works well as your expect, you have to migrate
    %s
and
    %s
by manual, or ask author for help
""" % (default_conf_full_path, instance_conf_full_path)

    print msg
    
def upgrade_config_file(proj_root_path):
    instance_conf_full_path = os.path.join(proj_root_path, "conf.py")
    default_conf_full_path = os.path.join(ZW_MOD_FULL_PATH, "default_conf.py")

    if ZW_MOD_FULL_PATH not in sys.path:
        sys.path.insert(0, ZW_MOD_FULL_PATH)
    default_conf_mod = __import__("default_conf")

    if proj_root_path not in sys.path:
        sys.path.insert(0, proj_root_path)
    instance_conf_mod = __import__("conf")


    ignore_fields = ("maintainer_email", "maintainer_email_suffix", "maintainer_email_prefix")

    # make sure conf.py (not conf.pyc) exists
    if instance_conf_mod and os.path.exists(instance_conf_full_path):
        changes_buf = ""

        for key, val in default_conf_mod.__dict__.iteritems():
            if key in ignore_fields:
                continue

            if key not in instance_conf_mod.__dict__:
                if isinstance(val, basestring):
                    changes_buf += key + " = '" + str(val) + "' \n"
                elif isinstance(val, (int, long)):
                    changes_buf += key + " = " + str(val) + "\n"

        if changes_buf:
            print
            print "new changes"
            print
            print changes_buf

            ans = raw_input("append above into instance's conf.py? [y/N] ")

            if ans in ("Y", "y"):
                with open(instance_conf_full_path) as f:
                    old_buf = f.read()

                if old_buf.find("coding:utf-8") == -1:
                    header = "#!-*- coding:utf-8 -*- \n"
                else:
                    header = ""

                with open(instance_conf_full_path, "w") as f:
                    data = header + old_buf + changes_buf
                    f.write(data)

            sys.stdout.write("\n")

            return True
        else:
            print
            print "no changes"
            print

            return False
    else:
        print "instance's conf.py doesn't, copy everything from origin"
        shutil.copy(default_conf_full_path, proj_root_path)

        return True

def upgrade_template_files(proj_root_path):
    cp_folder_templates(ZW_MOD_FULL_PATH = ZW_MOD_FULL_PATH, proj_root_path = proj_root_path)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 3:
        action, option = sys.argv[1], sys.argv[2]
        path = option

        if action == "create":
            if not os.path.exists(path):
                os.makedirs(path)

            proj_root_path = os.path.realpath(path)
            action_create(proj_root_path)
            exit(0)

        elif action == "upgrade":
            proj_root_path = os.path.realpath(path)
            action_upgrace(proj_root_path)
            exit(0)

    print_zwadmin_help_msg()
