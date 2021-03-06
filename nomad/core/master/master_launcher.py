import argparse

from nomad.core.config import ClientConfig
from nomad.core.master.master import Master
from nomad.core.universe.universe import Universe


def launch_master(args, kwargs):
    return Master(*args, **kwargs)  # Blocking call


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Launches the nomad client.')
    parser.add_argument('--rpc_port', type=int, help='RPC port for the master.', default=ClientConfig.RPC_DEFAULT_PORT)
    args = parser.parse_args()
    print("Starting nomad master")
    master_args = []
    master_kwargs = {'master_rpc_port': int(args.rpc_port)}#,
                     #'debug': True}
    master = launch_master(master_args, master_kwargs)
