import p2p_local as p2p # Included w/ application
import bluetooth
import json
import argparse
import logging
import socket
import copy
import os
import xmlrpc.client as xmlc

# Constants
_allowed = ['central','wireless']

class MultiSync: # Main MultiSync class
    def __init__(self,methods,config):
        # set inst vars
        self.methods = methods
        self.config = config
        self.central_cfg = copy.deepcopy(self.config['central'])
        self.tlds = [os.path.join(*i.split('.')) for i in self.config['toSync']]

        # Setup based on enabled methods, if any is required
        if 'wireless' in self.methods:
            logging.info(f'Starting p2p node on {config["wireless"]["name_prefix"] + socket.gethostname()}...')
            self.p2p_node = p2p.Node(
                config['wireless']['server_port'],
                config['wireless']['client_port'],
                config['wireless']['name_prefix'] + socket.gethostname(),
                protocol=config['wireless']['network']
            )
            logging.info(
                f"Started local p2p node on ports [{str(config['wireless']['server_port'])}, {str(config['wireless']['client_port'])}] in network {config['wireless']['network']}."
            )
        else:
            logging.info('Local P2P Connections Disabled.')
            self.p2p_node = None
        logging.debug('\n - '.join([
            'MultiSync Setup Complete. Details:',
            f'TLDs (Processed): [{", ".join(self.tlds)}]',
            f'Enabled Methods: [{", ".join(self.methods)}]'
        ]))
    
    def start(self):
        logging.info('Started MultiSync.')

if __name__ == '__main__': # On run
    args = argparse.ArgumentParser(description='Load MultiSync')
    args.add_argument('--config', help='Path to config file.');
    args.add_argument('--log', help='Logging level.', default='NOTSET');
    args.add_argument('--media', help='Transfer methods to use. Any number of [central, wireless] in priority order. Leave blank for all.', default=_allowed[:], nargs='*');
    args = args.parse_args()

    if not args.log.upper() in ['NOTSET','DEBUG','INFO','WARNING','ERROR','CRITICAL']:
        args.log = 'NOTSET'

    logging.basicConfig(level=args.log, format='%(levelname)s:%(message)s')

    _allowed_methods = args.media
    allowed_methods = []
    for i in _allowed_methods:
        if i in _allowed:
            allowed_methods.append(i)
    if len(allowed_methods) == 0:
        allowed_methods = _allowed[:]

    logging.info(f'Starting MultiSync. Running with config "{args.config}" on media [{", ".join(allowed_methods)}].')
    with open(args.config, 'r') as f:
        config = json.load(f)

    logging.debug('\n - '.join([
        'Configuration Details:',
        f'TLDs to Sync: [{", ".join(config["toSync"])}]',
        f'Peers: [{", ".join(config["peers"])}]',
        f'TLD Check Interval: {str(config["checkInterval"])} seconds'
    ]))

    multisync = MultiSync(allowed_methods,config)
    multisync.start()