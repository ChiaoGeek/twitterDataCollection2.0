#!/usr/bin/env python
# encoding: utf-8
"""
Created by Zhao Chang on 2017-12-07-16:16 in Los Angeles
Copyright (c) 2017 ACT. All rights reserved.
"""
from AccountAuthenticationClass import AccountAuthenticationClass
from MongoClass import MongoClass

import Queue
import tweepy
import yaml
import time
import datetime
import json
import gevent
import sys
import gevent.monkey
gevent.monkey.patch_socket()
gevent.monkey.patch_ssl()

#basic value
db_name = 'twitterTrends2'
tweets_collection = 'topTweets'
trends_collection = 'topTrends'
trends_has_collection = 'topTrendsCollection'
now_date = datetime.datetime.now() #2017-11-19 14:08:52.663697
date = str(now_date.year) + str(now_date.month) + str(now_date.day)

INITIALIZATION_STATIC = 0



#instantization
accountAuth = AccountAuthenticationClass().authenticationQueue()
monogoClient = MongoClass(db_name)

condition_queue = Queue.PriorityQueue()


def initialization(condition_queue):
    print "The program are initializing"

    global INITIALIZATION_STATIC

    if not INITIALIZATION_STATIC:
        print 'generate queue from trends collection'
        await_top_trends_collection = monogoClient.findAll(trends_has_collection, {})
        for y in await_top_trends_collection:
            condition_queue.put((y['priority'], y))

        INITIALIZATION_STATIC = INITIALIZATION_STATIC + 1

    await_top_trends = monogoClient.findAll(trends_collection, {'if_collecting': 0})
    # get new trends from topTrends and generate queue
    for x in await_top_trends:

        datetime = time.time()

        condition_put = {
            'trend_name': x['trend_name'],
            'max_id': -1,
            'since_id': 0,
            'initialization_max_id': 0,
            'datetime:': datetime,
            'priority': datetime,
            'location': x['location']
        }

        condition_queue.put((condition_put['priority'], condition_put))

        x['if_collecting'] = 1
        update_return_id = monogoClient.updateData(
            trends_collection,
            {'trend_name': x['trend_name']},
            x
        )

        if_exit =  monogoClient.findAll(trends_has_collection, {'trends_name': x['trend_name']}).count()
        if not if_exit:
            insert_return_id = monogoClient.insertOne(trends_has_collection, condition_put)


    print "Initialization has finished"
    return 1


def collectTtweets(condition_queue, accountAuth):


    while True:

        condition_get = list(condition_queue.get())[1] # Get the condition of search
        # print condition_get
        accountAuth_dict = accountAuth.get()
        accountAuth.put(accountAuth_dict)
        print accountAuth_dict['name']

        twitterAPI = accountAuth_dict['auth'] # obatin authentication

        try:
            new_tweets = twitterAPI.search(q=condition_get['trend_name'], count=100, max_id=str(condition_get['max_id']),
                                           since_id=str(condition_get['since_id']), lang="en", result_type="recent")
            if not new_tweets:

                print 'new_tweets empty'

                datetime = time.time()
                condition_put = {
                    'trend_name': condition_get['trend_name'],
                    'max_id': -1,
                    'since_id': condition_get['initialization_max_id'],
                    'initialization_max_id': 0,
                    'datetime:': datetime,
                    'priority':  datetime,
                    'location': condition_get['location']
                }
                update_return_id = monogoClient.updateData(
                    trends_has_collection,
                    {'trend_name': condition_get['trend_name']},
                    condition_put
                ) # update condition
                condition_queue.put((condition_put['priority'], condition_put))
            else:
                print 'has collected data'
                for i in new_tweets:
                    insert_data = {
                        'data': date,
                        'origin': json.dumps(i._json),
                        'location': condition_get['location'],
                        'trend_name': condition_get['trend_name']
                    }
                    insert_return_id = monogoClient.insertOne(tweets_collection, insert_data)
                # insert db

                datetime = time.time()


                condition_put = {
                    'trend_name': condition_get['trend_name'],
                    'max_id': new_tweets[-1].id - 1,
                    'since_id': condition_get['since_id'],
                    'datetime:': datetime,
                    'initialization_max_id': condition_get['initialization_max_id'],
                    'priority': 0 - datetime,
                    'location': condition_get['location']
                }


                if condition_get['initialization_max_id'] == 0:
                    condition_put['initialization_max_id'] = new_tweets[0].id - 1
                else:
                    condition_put['initialization_max_id'] = condition_get['initialization_max_id']

                monogoClient.updateData(trends_has_collection, {'trend_name': condition_get['trend_name']},
                                        condition_put)

                condition_queue.put((condition_put['priority'], condition_put))
                print 'OK'

        except tweepy.TweepError as e:

            print 'Tweepy error'
            print accountAuth_dict['name']
            print e
            datetime = time.time()
            condition_get['datetime'] = datetime

            condition_get['priority'] = datetime
            condition_queue.put((condition_get['priority'], condition_get))

            # try:
            #
            #     if e[0].code == 88:
            #
            #         condition_get['priority'] = 0 - datetime
            #         condition_queue.put((condition_get['priority'], condition_get))
            #
            #         # collectTtweets(condition_queue, accounAuth) # recursive
            #
            #     else:
            #         condition_get['priority'] = datetime
            #         condition_queue.put((condition_get['priority'], condition_get))
            #
            #     # condition_get['priority'] = 0 - datetime
            #     # condition_queue.put((condition_get['priority'], condition_get))


            # except:
            #
            #     print 'Error: '
            #     print sys.exc_info()[0]



                # collectTtweets(condition_queue, accounAuth)  # recursive

if __name__=='__main__':

    a = 0

    a = initialization(condition_queue)
    if a:
        print "Begining collecting --..--..--..--"
        #
        coroutine_tasks = [gevent.spawn(collectTtweets, condition_queue, accountAuth) for i in range(1)]
        gevent.joinall(coroutine_tasks)

    # print condition_queue.qsize()
    #
    # while not condition_queue.empty():
    #
    #     # print list(condition_queue.get())[1]['trend_name']
    #     print condition_queue.get()



