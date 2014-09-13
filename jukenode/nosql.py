import sys

import datetime
import traceback

from www.jukenode import settings

from pymongo import Connection, ASCENDING, DESCENDING, objectid
from pymongo.code import Code
from gridfs import GridFS
from flask.helpers import send_file
from io import BytesIO
from id3reader import Reader as ID3


__all__ =  ['GridFile', 'Collection', 'get_db']

def get_db(db_name, size=None):
    db =Connection(
        settings.NOSQL_HOST,
        settings.NOSQL_PORT,
        network_timeout=5,
    )\
        [db_name]
    return db



class GridFile(object):
    def __init__(self, db=None):
        if db:
            self.db = db
        self.gfs = GridFS(database=self.db)

    def delete(self, file_id):
        self.gfs.delete(file_id=objectid.ObjectId(file_id))

    def get(self, file_id):
        return self.gfs.get(file_id=objectid.ObjectId(file_id))

    def list(self):
        return self.gfs._GridFS__files.find().sort('uploadDate')

    def save_flask_upload(self, file_store):
        assert file_store.__class__.__name__ == 'FileStorage'
        r = ID3(file_store)
        kwargs = {}
        for key in ('album', 'performer', 'title', 'track', 'year', 'genre'):
            val = r.getValue(key)
            if val:  kwargs[key] = val

        file_store.seek(0)
        _id = self.gfs.put(
            filename= file_store.filename,
            content_type=file_store.content_type,
            data=file_store.stream,
            **kwargs
        )
        return _id

    def send_flask_file(self, grid_out):
        assert grid_out.__class__.__name__ == 'GridOut'
        byt = BytesIO(grid_out.read())
        return send_file(byt, mimetype=grid_out.content_type)


class Collection(object):
    timestamp = datetime.datetime.now

    def __init__(self, col_name=None, db=None):
        if db:
            self.db = db

        if col_name:
            self.col_name = col_name

        if not hasattr(self, 'pk_fields'):
            self.pk_fields = ['_id']

        self.col = self.db[self.col_name]
        self.col.ensure_index(
            [(key, 1) for key in self.pk_fields], unique=True
        )
        if hasattr(self, 'ensure_index'):
            for idx in self.ensure_index:
                self.col.ensure_index([idx])


    def insert(self, doc):
        assert type(doc) == dict
        return  self.col.insert(doc, safe=True)

    def save(self, doc, is_upsert=True):
        assert type(doc) == dict
        if '_id' in doc:
            _id = doc['_id']
            self.col.update({'_id': _id}, doc, safe=True)
        elif all([(i in doc) for i in self.pk_fields]):
            self.keys = dict([ (key, doc[key]) for key in self.pk_fields])
            self.col.update(self.keys, doc, upsert=is_upsert, safe=True)
            _id = None
        else:
            _id = self.col.insert(doc, safe=True)
        return _id

    def update(self, *args, **kwargs):
        return self.col.update(*args, **kwargs)

    def remove(self, **kwargs):
        self.col.remove(kwargs)
        return {'removed' : kwargs}

    def drop(self):
        self.db.drop_collection(self.col_name)

    def get_items(self, **kwargs):
        return { 'items' : [i for i in self.col.find(kwargs)] }

    def find(self, **kwargs):
        return self.col.find(kwargs) or {}

    def get_one(self, **kwargs):
##        if '_id' in kwargs:
##            kwargs['_id'] = objectid.ObjectId(kwargs['_id'])
        return self.col.find_one(kwargs) or {}
