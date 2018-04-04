#Ryan Sherry, Cletus Andoh,
#Cis 400
#Introduction to Social Media Data Mining
#Final Project
#4/4/2018

from datetime import datetime
import twitter
import json
import operator
import json
import networkx as nx
import pandas as pd   # handle data
from textblob import TextBlob  #sentiment analysis
import re

import numpy as np #for number computing

def oauth_login():
    
    CONSUMER_KEY = ''
    CONSUMER_SECRET = ''
    OAUTH_TOKEN = ''
    OAUTH_TOKEN_SECRET = ''    
    auth = twitter.oauth.OAuth(OAUTH_TOKEN, OAUTH_TOKEN_SECRET, CONSUMER_KEY, CONSUMER_SECRET)
    
    twitter_api = twitter.Twitter(auth=auth)
    return twitter_api

from functools import partial
from sys import maxint

# code from https://dev.to/rodolfoferro/sentiment-analysis-on-trumpss-tweets-using-python-
# code used from there includes clean_tweet and analise_sentiment

def clean_tweet(tweet):
    '''
    Utility function to clean the text in a tweet by removing 
    links and special characters using regex.
    '''
    return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

def analize_sentiment(tweet):
    '''
    Utility function to classify the polarity of a tweet
    using textblob.
    '''
    analysis = TextBlob(clean_tweet(tweet))
    if analysis.sentiment.polarity > 0:
        return 1
    elif analysis.sentiment.polarity == 0:
        return 0
    else:
        return -1

#original code from cookbook fro CIS 400SU
def twitter_search(twitter_api, q, max_results=200, **kw):

    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets and 
    # https://dev.twitter.com/docs/using-search for details on advanced 
    # search criteria that may be useful for keyword arguments
    
    # See https://dev.twitter.com/docs/api/1.1/get/search/tweets    
    search_results = twitter_api.search.tweets(q=q, count=100, **kw)
    
    statuses = search_results['statuses']
    
    # Iterate through batches of results by following the cursor until we
    # reach the desired number of results, keeping in mind that OAuth users
    # can "only" make 180 search queries per 15-minute interval. See
    # https://dev.twitter.com/docs/rate-limiting/1.1/limits
    # for details. A reasonable number of results is ~1000, although
    # that number of results may not exist for all queries.
    
    # Enforce a reasonable limit
    max_results = min(1000, max_results)
    
    for _ in range(10): # 10*100 = 1000
        try:
            next_results = search_results['search_metadata']['next_results']
        except KeyError, e: # No more results when next_results doesn't exist
            break
            
        # Create a dictionary from next_results, which has the following form:
        # ?max_id=313519052523986943&q=NCAA&include_entities=1
        kwargs = dict([ kv.split('=') 
                        for kv in next_results[1:].split("&") ])
        
        search_results = twitter_api.search.tweets(**kwargs)
        statuses += search_results['statuses']
        
        if len(statuses) > max_results: 
            break
            
    return statuses

#usage of code

tCount = 100  #number of tweets to be collected

twitter_api = oauth_login()

q = "Rugby"
results = twitter_search(twitter_api, q, max_results=tCount)

# Show one sample search result by slicing the list...
#print json.dumps(results[1], indent=1)

result2 = []

#harvest data from json 
x = 0 
while x < tCount:
	result2.append(results[x]['text'])
	#print x
	x+=1

#print result2 

#create Data Frame
data = pd.DataFrame(data= result2, columns=['Tweets'])

#Display the first 10 elements of the data frame
#display(data.head(10))

#prints all elements of the dataFrame
#print data.values

# add length coloumn to data frame for each tweet
data['len'] = np.array([len(result2[tweet]) for tweet in range(tCount)])
data['SA'] = np.array([ analize_sentiment(tweet) for tweet in data['Tweets'] ])

#print "length" 
#print data.values

#sentiment analysis for tweet
pos_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] > 0]
neu_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] == 0]
neg_tweets = [ tweet for index, tweet in enumerate(data['Tweets']) if data['SA'][index] < 0]

print "SENTIMENT ANALYSIS OF '%s' for '%s' number of tweets" % (q, tCount)
print("Percentage of positive tweets: {}%".format(len(pos_tweets)*100/len(data['Tweets'])))
print("Percentage of neutral tweets: {}%".format(len(neu_tweets)*100/len(data['Tweets'])))
print("Percentage of negative tweets: {}%".format(len(neg_tweets)*100/len(data['Tweets'])))
