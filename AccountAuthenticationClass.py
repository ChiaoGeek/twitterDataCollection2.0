#!/usr/bin/env python
# encoding: utf-8
"""
This file is used to realize authentication

Created by Zhao Chang on 2017-12-07-13:22 in Los Angeles
Copyright (c) 2017 ACT. All rights reserved.
"""

import tweepy, yaml, Queue

class AccountAuthenticationClass:

    def __init__(self):

        self.configure = yaml.load(open('TwitterAccount.yml'))

    def authenticationQueue(self):

        q = Queue.Queue()

        for x in self.configure['authentication'].items():
            self.auth = tweepy.OAuthHandler(x[1]['consumer_key'],x[1]['consumer_secret'])
            self.auth.set_access_token(x[1]['access_token'], x[1]['access_token_secret'])
            self.api = tweepy.API(self.auth)
            dict = {}
            dict['name'] = x[0]
            dict['auth'] = self.api
            q.put(dict)

        return q


    def singleAuthentication(self):

        return self.authenticationQueue().get()


if __name__  == '__main__':

    aac = AccountAuthenticationClass()
    res = aac.authenticationQueue()
    print type(res)
    print res
    while True:
        accountAuth_dict = res.get()
        #
        print accountAuth_dict['name']
        res.put(accountAuth_dict)