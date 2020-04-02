from Crypto.PublicKey import RSA
from Crypto import Random
from flask import Flask, request
import requests
import simplejson as json


from blockchain import Blockchain
from block import Block
from state import state
from transaction import Transaction
from config import * 



app = Flask(__name__)


#------------------------------------------------------------
# BROADCASTING

def broadcast_block(block,node_id = None) :
    json_block = block.to_json()
    return broadcast(json_block,'receive_block',node_id)

def broadcast_transaction(t,node_id = None ) :
    json_t = t.to_json()
    return broadcast(json_t,'receive_transaction',node_id)


def broadcast(json_obj,rest_point,node_id = None):
    """ Broadcast object to network """
    if node_id == None :
        broadcast_nodes = state.nodes 
    else :
        broadcast_nodes = [state.nodes[node_id]]

    for node in broadcast_nodes:
        #broadcast to everyone except sender
        if (node['pub'] == state.pub):
            continue
        ip = node["ip"]
        port = node["port"]
        response = requests.post(f'http://{ip}:{port}/{rest_point}', json=json_obj)
        if (response.status_code != 200):
            return False
    return True


def broadcast_nodes_info():
    '''
    when all nodes are in the state.nodes dictionary,
    notify all nodes about the others
    '''
    json_nodes = json.dumps(state.nodes)
    return broadcast(json_nodes)    
    return True
    
def new_transaction(receiver, amount):
    #creates t, the new transaction, and broadcasts it
    t = Transaction.create_transaction(receiver, amount)
    return broadcast_transaction(t)

# ------------------------------------------

##? What do these return? Some sort of status code? 
##? Some values? 

@app.route('/receive_block', methods=['POST'])
def receive_block(json_string):
    block =  Block(**json.loads(json_string))
    # pass to Blockchain to add block
    return state.blockchain.add_block()

    
@app.route('/receive_transaction', methods=['POST'])
def receive_transaction(json_string):
    # Call static method, object creation is handled in function
    return_val,t = Transaction.validate_transaction(json_string)
    if return_val :
        state.transactions.append(t)
    return return_val
    

@app.route('/register_node', methods=['POST'])
def register_new_node():
    '''
    An incoming node posts a request to enter the network 
    - Handle request and post in return 
    '''
    data = request.get_json()
    node_ip = data['ip']
    node_port = data['port']
    node_pubkey = data['pub']
    if (not node_ip or not node_port or not node_pubkey):
        return "Invalid", 400
    
    maxid = max(state.nodes, key=int)
    new_id = maxid + 1
    state.nodes[new_id]['ip'] = node_ip
    state.nodes[new_id]['port'] = node_port
    state.nodes[new_id]['pubkey'] = node_pubkey
    
    # broadcast 100 NBC
    #sync the new node with the blockchain, by broadcasting chain
   

    if new_transaction(node_pubkey,100):
        return json.dump(new_id)
    

# A node requests the chain via a GET request , we return the chain
@app.route('./request_chain',methods=['GET'])
def request_chain():
    block_list = [block.to_json() for block in state.blockchain]        
    json_chain = json.dumps({"chain": block_list})
    return json_chain 

