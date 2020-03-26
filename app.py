# Dependences
from flask import Flask, Response, request, current_app, abort
from flask_cors import CORS
from datetime import datetime, timedelta
from flask_jwt import JWT, JWTError, jwt_required, current_identity, _jwt
from werkzeug.exceptions import HTTPException
from functools import wraps, partial
import os
import json

import traceback
#import uuid
#import pymongo
import glob2
from config import *
from dataset import PretrainedSpacyDataset, PaperWord2VecDataset
from threading import Thread

# Start APP
app = Flask(__name__)
CORS(app)
SERVER_PORT = 7575

# Load dataset
dataset = PretrainedSpacyDataset(dataset_path=DATASET_PICKLE, vectors_dataset_path=SCAPY_PRETRAINED_VECTORS_DATASET_PICKLE, num_dimensions=200, mode='compare', use_faiss=False)
def back_sync():
    dataset.sync('allen-institute-for-ai/CORD-19-research-challenge', RAW_DATASET_PATH)
Thread(target=back_sync).start()

"""
==========================================0
    USERS
==========================================0
"""
from werkzeug.security import safe_str_cmp
from functools import wraps
def authenticate(username, password):
    data = json.loads(request.data)
    user = User.get(username=username)
    if not (user and safe_str_cmp(user.password.encode('utf-8'), User.cypher(password).encode('utf-8'))):
        return

    if 'group' in data and data['group'] != user.group:
        raise JWTError('Bad Request', 'Invalid group')

    if not user.enable:
        raise JWTError('Bad Request', 'Removed user')

    user.ref_id = str(user.ref_id)
    return user

def identity(payload):
    user_id = payload['identity']
    user = User.get(ref_id=user_id)
    user.ref_id = str(user.ref_id)
    return user

def group_decorator(group=None, groups=[]):
    if group is not None:
        groups = [group]
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            if current_identity.group not in groups:
                raise JWTError('Bad Request', 'Invalid group')
            return fn(*args, **kwargs)
        return decorator
    return wrapper

"""
==========================================0
    APP
==========================================0
"""
@app.route('/init', methods=["GET"])
def init():
    return {
        'algorithms': [
            'WORD2VEC',
            'FASTTEXT'
        ]
    }

@app.route('/search', methods=["POST"])
def search():
    data = json.loads(request.data)
    search_query = data['query']
    documents = dataset.get_similar_docs_than(search_query, k=300)

    documents_return = []
    for i, doc in enumerate(documents):
        documents_return.append({
            'rank': i,
            'reference_id': doc.id,
            'title': doc.title,
            'abstract': doc.abstract,
            'body': doc.body
        })

    return {
        'documents': documents_return
    }

if __name__ == '__main__':
    app.run(port=SERVER_PORT)