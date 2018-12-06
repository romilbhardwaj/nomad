import argparse

from nomad.core.client.client import NomadClient
from nomad.core.config import ClientConfig


def launch_client(args, kwargs):
    return NomadClient(*args, **kwargs)  # Blocking call


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launches the nomad client.')
    parser.add_argument('guid', type=str, help='GUID of the client.')
    parser.add_argument('masterrpc', type=str, help='RPC addr of the master. Eg. http://127.0.0.1:20000')
    parser.add_argument('--operator_path', type=str, help='Path of the operator.', default='/nomad/op.pickle')
    parser.add_argument('--rpc_port', type=int, help='RPC port for the client.', default=ClientConfig.RPC_DEFAULT_PORT)
    parser.add_argument('--next_op_addr', type=str, help='RPC port for the client.', default=None)
    parser.add_argument('--is_first', action='store_true', default=False)
    parser.add_argument('--is_final', action='store_true', default=False)
    parser.add_argument('--debug', action='store_true', default=False)
    args = parser.parse_args()
    print("Starting nomad client")
    client_args = [args.guid, args.masterrpc]
    client_kwargs = {'client_rpc_port': int(args.rpc_port),
                     'operator_path': str(args.operator_path),
                     'next_op_addr': str(args.next_op_addr),
                     'is_first_operator': bool(args.is_first),
                     'is_final_operator': bool(args.is_final),
                     'debug': bool(args.debug)
                     }
    client = launch_client(client_args, client_kwargs)
