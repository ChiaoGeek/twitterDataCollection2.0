#!/usr/bin/env python
# encoding: utf-8
"""
Created by Zhao Chang on 2017-12-17-10:42 in Los Angeles
Copyright (c) 2017 ACT. All rights reserved.
"""
from pymongo import MongoClient


def migrateData(origin, new):
    client = MongoClient('localhost', 27017)

    new_db = client[new['db']]
    origin_db = client[origin['db']]

    new_collection = new_db[new['collection']]
    origin_collection = origin_db[new['collection']]

    a = 1

    for i in origin_collection.find():
        a = a + 1
        if a > 2:
            break
        print new_collection.insert_one(i).inserted_id


origin = {
    'db': 'twitterTrends',
    'collection': 'topTrends'
}
new = {
    'db': 'twitterTrends2',
    'collection': 'topTrends'
}


migrateData(origin, new)


