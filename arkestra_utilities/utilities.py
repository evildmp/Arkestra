import pickle
import hashlib


def generate_key(*args, **kwargs):
    return hashlib.sha224(pickle.dumps([args, kwargs])).hexdigest()
