#!/usr/bin/env python
# encoding: utf-8
"""
Created by Zhao Chang on 2017-12-18-10:55 in Los Angeles
Copyright (c) 2017 ACT. All rights reserved.
"""
from pymongo import MongoClient

import yaml

class MongoClass:

    def __init__(self, db_name):
        self.configure = yaml.load(open('configure.yml'))
        self.mongo_client = MongoClient(self.configure['mongoDB']['address'], self.configure['mongoDB']['port'])
        self.db = self.mongo_client[db_name]

    def insertOne(self, collection_name, data):
        collection = self.db[collection_name]
        return collection.insert_one(data).inserted_id

    def findAll(self, collection_name, query):
        collection = self.db[collection_name]
        return collection.find(query)

    def updateData(self, collection_name, query, data):
        collection = self.db[collection_name]
        return collection.update(query, data, upsert = True)

