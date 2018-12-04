def merge_dicts(x, y):
    z = x.copy()
    z.update(y)
    return z

def construct_xmlrpc_addr(ip, port):
    return "http://" + str(ip) + ":" + str(port)