from multisync_rpc_commands import certify_network
import p2p_local as p2p  # Included w/ application
import bluetooth, time
import json
import argparse
import logging
import socket
import copy
import os
from rpc_client import Client

# Constants
_allowed = ['central', 'wireless']


class MultiSync:  # Main MultiSync class
    def __init__(self, methods, config):
        # set inst vars
        self.methods = methods
        self.config = config
        self.central_cfg = copy.deepcopy(self.config['central'])
        self.tlds = [os.path.join(*i.split('.'))
                     for i in self.config['toSync']]

        # Setup based on enabled methods, if any is required
        if 'wireless' in self.methods:
            logging.info(
                f'Starting p2p node on {config["wireless"]["name_prefix"] + socket.gethostname()}...')
            self.p2p_node = p2p.Node(
                config['wireless']['server_port'],
                config['wireless']['client_port'],
                config['wireless']['name_prefix'] + socket.gethostname(),
                protocol=config['wireless']['network']
            )
            logging.info(
                f"Started local p2p node on ports [{str(config['wireless']['server_port'])}, {str(config['wireless']['client_port'])}] in network {config['wireless']['network']}. Discovered {str(len(self.p2p_node.discover(name=config['peers'])))} peers in network."
            )
        else:
            logging.info('Local P2P Connections Disabled.')
            self.p2p_node = None
        if 'central' in self.methods:
            logging.info(
                f'Starting RPC Command connection to {str(config["central"]["server"])} on MultiSync Network {config["central"]["network"]}.')
            self.rpc_client = Client({
                'server_url': f'http://{config["central"]["server"][0]}:{str(config["central"]["server"][1])}',
                'key': config["central"]["key"]
            })
            inf = self.rpc_client.get_module_info(key='multisync')
            if 'result' in inf.keys():
                if inf['result'] == 'key not found.':
                    self.rpc_client.add_module('multisync', {
                        "name": "MultiSync",
                        "type": "webfile",
                        "url": "https://raw.githubusercontent.com/iTecAI/MultiSync/main/multisync_rpc_commands.py",
                        "requirements": [],
                        "command_list": {
                            "get_sync_hash": "get_sync_hash",
                            "certify_network":"certify_network"
                        }
                    })
                    stage = None
                    while not stage in ['finished','failed']:
                        time.sleep(0.25)
                        stat = self.rpc_client.check_status('multisync')
                        stage = stat['stage']
                        logging.info(f'Installing MultiSync on server - Progress: {str(stat)}')
            self.rpc_client.command('multisync','certify_network',{'network':config['central']['network'],'tlds':[i.split('.').pop() for i in config['toSync']]})
            print(inf)
            logging.info(
                f'Loaded RPC Command connection to {str(config["central"]["server"])} on MultiSync Network {config["central"]["network"]}.')
        else:
            logging.info('Central Server Connections Disabled.')
            self.rpc_client = None

        logging.debug('\n - '.join([
            'MultiSync Setup Complete. Details:',
            f'TLDs (Processed): [{", ".join(self.tlds)}]',
            f'Enabled Methods: [{", ".join(self.methods)}]'
        ]))

    def start(self):
        logging.info('Started MultiSync.')


if __name__ == '__main__':  # On run
    args = argparse.ArgumentParser(description='Load MultiSync')
    args.add_argument('--config', help='Path to config file.')
    args.add_argument('--log', help='Logging level.', default='NOTSET')
    args.add_argument(
        '--media', help='Transfer methods to use. Any number of [central, wireless] in priority order. Leave blank for all.', default=_allowed[:], nargs='*')
    args = args.parse_args()

    if not args.log.upper() in ['NOTSET', 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        args.log = 'NOTSET'

    logging.basicConfig(level=args.log, format='%(levelname)s:%(message)s')

    _allowed_methods = args.media
    allowed_methods = []
    for i in _allowed_methods:
        if i in _allowed:
            allowed_methods.append(i)
    if len(allowed_methods) == 0:
        allowed_methods = _allowed[:]

    logging.info(
        f'Starting MultiSync. Running with config "{args.config}" on media [{", ".join(allowed_methods)}].')
    with open(args.config, 'r') as f:
        config = json.load(f)

    logging.debug('\n - '.join([
        'Configuration Details:',
        f'TLDs to Sync: [{", ".join(config["toSync"])}]',
        f'Peers: [{", ".join(config["peers"])}]',
        f'TLD Check Interval: {str(config["checkInterval"])} seconds'
    ]))

    multisync = MultiSync(allowed_methods, config)
    multisync.start()
