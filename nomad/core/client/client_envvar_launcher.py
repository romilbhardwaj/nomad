import os
from nomad.core.client.client import NomadClient
from nomad.core.config import ClientConfig


def launch_client(args, kwargs):
    return NomadClient(*args, **kwargs)  # Blocking call


def str2bool(v):
    return str(v).lower() in ("yes", "true", "t", "1")


def read_env_vars():
    guid = os.environ[ClientConfig.ENVVAR_GUID]
    masterrpc = os.environ[ClientConfig.ENVVAR_MASTERRPC]
    rpc_port = os.getenv(ClientConfig.ENVVAR_RPCPORT, ClientConfig.RPC_DEFAULT_PORT)
    next_op_addr = os.getenv(ClientConfig.ENVVAR_NEXT_OP_ADDR, '')
    operator_path = os.getenv(ClientConfig.ENVVAR_OPERATORPATH, ClientConfig.DEAFULT_OPERATOR_PATH)
    is_final = os.getenv(ClientConfig.ENVVAR_IS_FINAL, False)
    is_first = os.getenv(ClientConfig.ENVVAR_IS_FIRST, False)
    debug = os.getenv(ClientConfig.ENVVAR_DEBUG, False)
    pipeline_guid = os.environ[ClientConfig.ENVVAR_PIPELINE_GUID]
    if not isinstance(debug, bool):
        debug = str2bool(debug)
    if not isinstance(is_first, bool):
        is_first = str2bool(is_first)
    if not isinstance(is_final, bool):
        is_final = str2bool(is_final)

    client_args = [guid, masterrpc, pipeline_guid]
    client_kwargs = {'client_rpc_port': int(rpc_port),
                     'operator_path': str(operator_path),
                     'next_op_addr': str(next_op_addr),
                     'is_first_operator': bool(is_first),
                     'is_final_operator': bool(is_final),
                     'debug': bool(debug)
                     }
    return client_args, client_kwargs


if __name__ == '__main__':
    print("Starting nomad client")
    client_args, client_kwargs = read_env_vars()
    print("Read envvars.")
    print("args: %s" % client_args)
    print("kwargs: %s" % client_kwargs)
    client = launch_client(client_args, client_kwargs)
