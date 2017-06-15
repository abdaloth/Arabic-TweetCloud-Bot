#!/usr/bin/python3
import tweepy
import sys
import re
import arabic_reshaper
import numpy
import configparser
import atexit
from random import randint
from wordcloud import WordCloud
from stop_words import get_stop_words
from bidi.algorithm import get_display
from os import path
from PIL import Image


def get_config(ini_file):
    cfg = configparser.ConfigParser()
    cfg.read(ini_file)
    return cfg['twitokens'], cfg['paths']


def get_api(cfg):
    auth = tweepy.OAuthHandler(cfg['consumerkey'], cfg['consumersecret'])
    auth.set_access_token(cfg['accesstoken'], cfg['accesstokensecret'])
    return tweepy.API(auth)


def get_tweet_text(screen_name, api):

    tweets = api.user_timeline(screen_name=screen_name, count=200)
    alltweets = tweets
    oldest = alltweets[-1].id - 1

    # since max is 200 tweets per request , we will repeat this process until
    # we pass through the whole timeline
    while len(tweets) > 0:
        tweets = api.user_timeline(
            screen_name=screen_name, count=200, max_id=oldest)
        alltweets.extend(tweets)
        oldest = alltweets[-1].id - 1
        print("\rretrieved {} tweets from {}'s timeline".format(
            len(alltweets), screen_name), end='')

    tweettext = [tweet.text for tweet in alltweets]
    tweettext = " ".join(tweettext)
    return tweettext


def reshape_arabic_text(text):
    return get_display(arabic_reshaper.reshape(text))


def get_clean_text(text):
    emails = re.compile(r'\w+@\w+\.\w+')
    retweets = re.compile(r'(RT )?@[\w]+')
    links = re.compile(r'https?://.+?(\s|$)')
    symbols = re.compile(r'[^\w\s]')

    text = re.sub(emails, '', text)
    text = re.sub(retweets, '', text)
    text = re.sub(links, '', text)
    text = re.sub(symbols, ' ', text)

    return text


def create_masked_cloud(screen_name, text, mask_path, font_path):
    stopwords = get_stop_words('english')
    # TODO: fix problem in arabic stopwords (should I put it in the config?)
    arabic_stopwords = []
    for word in get_stop_words('arabic'):
        arabic_stopwords.append(reshape_arabic_text(word))
    stopwords.extend(arabic_stopwords)
    print('\ngenerating wordcloud...')
    cloud_mask = numpy.array(Image.open(mask_path))
    wc = WordCloud(font_path=font_path, background_color="white",
                   max_words=3000, mask=cloud_mask, stopwords=stopwords)
    wc.generate(text)
    wc.to_file(path.join(d, "output/{}_cloud.png".format(screen_name)))


def init():
    api.update_status("{} الحين مصحصح، ﻻ يردكم إللا المنشن!".format(randint(1,1337)))
    listener = myListener()
    stream = tweepy.Stream(auth=api.auth, listener=myListener())
    stream.filter(track=['tootbot سحابة,tootbot cloud'])


def end():
    api.update_status("أبي أطفي هالحين، نشوفكم على خير يا جماعة! {}".format(randint(1,1337)))


class myListener(tweepy.StreamListener):

    def on_status(self, status):
        print(status.text)
        screen_name = status.user.screen_name
        text = get_tweet_text(screen_name, api)
        clean_text = get_clean_text(text)
        reshaped_bidi_text = reshape_arabic_text(clean_text)
        create_masked_cloud(screen_name, reshaped_bidi_text,
                            mask_path, font_path)
        api.update_with_media("output/{}_cloud.png".format(screen_name),
                              status="@{} سم، هذي سحابتك".format(screen_name),  in_reply_to_status_id=status.id)


d = path.dirname('__file__')
tokens, paths = get_config('cfg.ini')
api = get_api(tokens)
mask_path = paths['mask']
font_path = paths['font']



atexit.register(end)
init()
