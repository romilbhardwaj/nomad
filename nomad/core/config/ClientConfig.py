DEFAULT_LOG_DIR = '/nomad/log'
CLIENT_LOG_FILE_NAME = 'nomad_client.log'

OPERATOR_BASE_PATH = '/nomad/nomad/tests/operators/'
DEAFULT_OPERATOR_PATH = '/nomad/operator.pickle'

RPC_DEFAULT_PORT = 30000
RPC_INIT_WAIT_INTERVAL = 5

MAX_INCOMING_QUEUE_SIZE = 10
MAX_OUTGOING_QUEUE_SIZE = 10

RETRY_SLEEP_DURATION = 1

# Specify names of envvars to use in the docker container.
ENVVAR_GUID = 'GUID'
ENVVAR_MASTERRPC = 'MASTERRPC'
ENVVAR_RPCPORT = 'RPCPORT'
ENVVAR_OPERATORPATH = 'OPERATOR_PATH'
ENVVAR_NEXT_OP_ADDR = 'NEXT_OP_ADDR'
ENVVAR_IS_FIRST = 'IS_FIRST'
ENVVAR_IS_FINAL = 'IS_FINAL'
ENVVAR_DEBUG = 'DEBUG'