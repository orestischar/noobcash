# -*- coding: utf-8 -*-
'''
application in order to send requests and perform functions

usage:

python start_app.py HOST PORT --l COORD_HOST --lp COORD_PORT: start a client and coordinate it to the coordinator.
python start_app.py HOST PORT --c CLIENTS --m MONEY: start the coordinator,
with a capacity of CLIENTS clients and give them MONEY money in the wallet.

Also includes a full CLI implementation.
'''

import sys
import broadcast
import requests
import argparse
import simplejson as json
from state import state
from flask import Flask, request
from config import *

import click
import os

@click.group()

def cli():
    pass

parser = argparse.ArgumentParser()
parser.add_argument('host', type=str) #the host of the address 
parser.add_argument('port', type=int) #the port of the address
parser.add_argument('--c', type=int) #the number of clients (when running as coordinator)
parser.add_argument('--m', type=int) #the number of initial money (when running as coordinator)
parser.add_argument('--l', type=str) #the host of the coordinator address (when running as client)
parser.add_argument('--lp', type=str) #the port of the coordinator address (when running as client)
args = parser.parse_args()

HOST = f'http://{args.host}:{args.port}'
PORT = str(args.port)
CLIENTS = args.c
MONEY = args.m
COORDINATOR_HOST = args.l
COORDINATOR_PORT = args.lp
COORDINATOR_URL = f'http://{COORDINATOR_HOST}:{COORDINATOR_PORT}'
URL = f'{HOST}/start_coordinator' if CLIENTS else f'{COORDINATOR_URL}/register_node'

if (CLIENTS):
    IS_COORDINATOR = True
    response = requests.post(URL, json=json.dumps({'num_clients': str(CLIENTS), 'initial_money': str(MONEY),\
                             'host': HOST, 'port': str(PORT)}))
else:
    IS_COORDINATOR = False
    print(state.pub)
    response = requests.post(URL, json=json.dumps({'ip': HOST, 'port': str(PORT), 'pub': state.pub.exportKey().decode()}))

while(True):
    '''
    CLI implementation with click
    '''
    @cli.command()
    @click.option('--recipient_address', type=str)
    @click.option('--amount', type=float)
    def new_transaction(recipient_address, amount):
        '''
        

        Parameters
        ----------
        recipient_address : the address and the port
        the recipient is listening to, e.g. "127.0.0.1:5050"
        amount : the amount of cash the recipient
        will receive, e.g. "30"

        Returns
        -------
        todo
        203 if the request and the transaction was complete
        400 if the request was bad
        500 if the request was good but the transaction failed

        '''
        recipient_ip, recipient_port = recipient_address.split(':')
        for node in state.nodes.values():
            if node['ip'] == recipient_ip and node['port'] == recipient_port:
                node_pub = node['pubkey']
        
        if (broadcast.new_transaction(node_pub, amount)):
            return True
        else:
            return False
    
    @cli.command()
    def view():
        '''
        
        Parameters
        ----------
        None.
        
        Returns
        -------
        Prints the transactions in the last validated
        block of the chain. Calls view_transactions()
        functions that does this.
        
        '''
        state.view_transactions()
    
    @cli.command()
    def balance():
        '''
        
        Print the current balance of the wallet,
        by calculating UTXOs.
        
        '''
        print(state.wallet_balance())
    
    @cli.command()
    def help():
        
        '''
        explanation of the above commands
        '''
        
        pass
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    