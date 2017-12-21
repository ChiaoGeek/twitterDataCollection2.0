#!/usr/bin/env python
# encoding: utf-8
"""
Created by Zhao Chang on 2017-12-18-18:24 in Los Angeles
Copyright (c) 2017 ACT. All rights reserved.
"""
from MongoClass import MongoClass

#basic value
db_name = 'twitterTrends2'
tweets_collection = 'topTweets'
trends_collection = 'topTrends'
trends_has_collection = 'topTrendsCollection'

#initialization
mongo_client = MongoClass(db_name)

for x in mongo_client.findAll(trends_collection, {}):
    x['if_collecting'] = 0
    x['trend_name'] = "#LGBTbabes"
    print mongo_client.updateData(trends_collection, {'trend_name': '#LaVoixJunior'}, x)
    # print mongo_client.updateData(trends_collection, {'trend_name': x['trend_name']}, {'if_collecting': 1})