import functools

from config_agent import config
import commons
import web


def _check_ip(req_obj, req_path):
    # allow_ips = ("192.168.0.10", )
    allow_ips = commons.netutils.INVALID_REMOTE_IP_ADDRESSES
    remote_ip = web.ctx.get("ip")
    if not remote_ip:
        return False

    if not commons.ip_in_network_ranges(remote_ip, allow_ips):
        return False

    return True

def check_ip(f):
    @functools.wraps(f)
    def wrapper(req_obj, req_path):
        if _check_ip(req_obj, req_path):
            return f(req_obj, req_path)

        raise web.Forbidden()
    return wrapper


def _check_rw(req_obj, req_path):
    inputs = web.input()
    action = inputs.get("action", "read")

    if config.getboolean("main", "readonly"):
        if (action not in ("read", "source")) or (req_path == "~new"):
            return False

    return True

def check_rw(f):
    @functools.wraps(f)
    def wrapper(req_obj, req_path):
        if _check_rw(req_obj, req_path):
            return f(req_obj, req_path)
        raise web.Forbidden()
    return wrapper
