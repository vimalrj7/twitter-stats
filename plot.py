import plotly
import plotly.graph_objects as go
import numpy as np
import nltk
import pandas as pd
import ast
import re
import itertools
import collections
from textblob import TextBlob
import tweepy as tw
import os
import json

consumer_key= os.environ.get('consumer_key')
consumer_secret= os.environ.get('consumer_secret')
access_token= os.environ.get('access_token')
access_token_secret= os.environ.get('access_token_secret')

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True)

def get_tweets(screen_name):
    tweets = []
    FILE_PATH = 'data/'+screen_name+'.csv'
    if os.path.isfile(FILE_PATH):
        df = pd.read_csv(FILE_PATH)
        print('File found in cache.')
        return df

    print('Fetching data from Twitter...')
    for tweet in tw.Cursor(api.user_timeline, screen_name=screen_name, tweet_mode="extended", include_rts=False).items(2000):
        tweets.append(tweet)

    # convert 'tweets' list to pandas.DataFrame
    print(len(tweets))
    df = pd.DataFrame(vars(tweets[i]) for i in range(len(tweets)))
    df.to_csv(FILE_PATH)
    print("Complete.")

    return df
    
def get_hashtags(hashtag_array):
    """Get hashtags from column, put into string"""
    output = []
    for item in hashtag_array:
        output.append(item['text'])
    return "|".join(output)

def get_users_mentions(user_mentions_array):
    """Get user mentions from column, put into string"""
    output = []
    for item in user_mentions_array:
        output.append(item['screen_name'])
    return "|".join(output)

def construct_df(df):

    cols = ['created_at','display_text_range', 'entities', 'favorite_count', 'full_text', 'id_str', 'retweet_count', 'source']
    df = df[cols]
    df['created_at'] = pd.to_datetime(df['created_at'])
    df = df.astype({'source': 'category', 'id_str': 'str'})
    df['display_text_range'] = df['display_text_range'].apply(lambda x: ast.literal_eval(str(x))[1])

    df.columns = ['date', 'length', 'entities', 'favorites', 'tweet', 'id', 'retweets', 'source']
    df = df.join(pd.json_normalize(df['entities'].map(str).map(ast.literal_eval).tolist())).drop(['entities', 'symbols', 'media', 'urls'], axis=1)

    df.hashtags = df.hashtags.apply(get_hashtags)
    df.user_mentions = df.user_mentions.apply(get_users_mentions)
    df.tweet = df.tweet.str.replace("&amp;", "and")
    df = df.apply(lambda x: x.str.strip() if isinstance(x, str) else x).replace('', np.nan)

    print("Dataframe constructed.")
    
    return df

def top_freq(name, type, count, title):
    top_freq = collections.Counter(type).most_common(count)

    top_freq_df = pd.DataFrame(top_freq, columns=[name, 'freq'])

    #fig = px.bar(top_freq_df, x='Words', y='freq', hovertemplate='Hi!')
    fig = go.Figure(data=[go.Bar(x=top_freq_df[name], y=top_freq_df['freq'], 
                                hovertemplate="Used %{y} times<extra></extra>")])
    
    fig.update_layout(
    title=title,
    xaxis_title=name,
    yaxis_title="Number of times used")   
    
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON
    
    
def clean_tweet(tweet):
    """Removes links, hashtags and user mentions from the tweet, and returns it in lower case"""
    cleaned_tweet = " ".join(re.sub("(\w+:\/\/\S+)|(#\w+)|(@\w+)", "", tweet).split())    
    return cleaned_tweet

def top_words(df):
    tweets = [clean_tweet(x) for x in df.tweet.tolist()]
    tweet_words_with_punchuation = list(itertools.chain(*[nltk.word_tokenize(x) for x in tweets]))
    tweet_words = [word.lower() for word in tweet_words_with_punchuation if word.isalnum()]
    stop_words = nltk.corpus.stopwords.words('english')
    stop_words.extend(['would'])
    tweet_words_nsw = [word for word in tweet_words if not word in stop_words]

    return top_freq("Words", tweet_words_nsw, 10, 'Top 10 words used over all tweets')

def top_hashtags(df):
    df.hashtags.dropna().str.split('|').tolist()
    hashtags = list(itertools.chain(*df.hashtags.dropna().str.split('|').tolist()))
    hashtags = ['#'+x for x in hashtags]

    return top_freq("Hashtags", hashtags, 10, 'Top 10 hashtags used over all tweets')


def top_users(df):
    df.user_mentions.dropna().str.split('|').tolist()
    user_mentions = list(itertools.chain(*df.user_mentions.dropna().str.split('|').tolist()))
    user_mentions = ['@'+x for x in user_mentions]

    return top_freq("User Mentions", user_mentions, 10, "Top 10 user mentions over all tweets")

def favorite_days(df):
    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dg = df.groupby(df.date.dt.day_name())
    weekday = dg.tweet.count().reindex(days)
    
    fig = go.Figure(data=[go.Bar(x=days, y=weekday, 
                                hovertemplate="%{y} Tweets<extra></extra>")])
    
    fig.update_layout(
    title="Number of tweets by day",
    xaxis_title="Day",
    yaxis_title="Number of tweets")   
    
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    return graphJSON
    
def tweet_sentiment(df):
    tweets = [clean_tweet(x) for x in df.tweet.tolist()]
    sentiment_objects = [TextBlob(tweet) for tweet in tweets]
    sentiment_values = [tweet.sentiment.polarity for tweet in sentiment_objects]
    df['sentiment'] = sentiment_values
    df_sentiment = df.query("(sentiment != 0)")
    # Plot histogram of the polarity value
    df_hist = df_sentiment['sentiment']    
    fig = go.Figure(data=[go.Histogram(x=df_hist)])   
    
    fig.update_layout(
    title="Overall Tweeter Sentiment",
    xaxis_title="Tweet Sentiment (negative to positive)",
    yaxis_title="Number of tweets")   
    
    graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return graphJSON
    
def create_plots(screen_name):
    plots = []


    tweets = get_tweets(screen_name)
    df = construct_df(tweets)

    words = top_words(df)
    plots.append(words)

    hashtags = top_hashtags(df)
    plots.append(hashtags)

    users = top_users(df)
    plots.append(users)

    days = favorite_days(df)
    plots.append(days)

    sent = tweet_sentiment(df)
    plots.append(sent)

    return plots