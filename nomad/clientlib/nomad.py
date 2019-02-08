import cloudpickle
import xmlrpc.client

def submit_pipeline(ops, start, end, pid, master_ip):
    server = xmlrpc.client.ServerProxy(master_ip)
    data_to_send = []

    #pickle operators
    for op in ops:
        p = cloudpickle.dumps(op)
        data_to_send.append(p)

    server.receive_pipeline(data_to_send, start, end, pid)




