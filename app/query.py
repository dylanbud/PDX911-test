import dotenv
import numpy as np
import pandas as pd
import flask
import tweepy
from os import getenv
import os
from dotenv import load_dotenv
import requests
import urllib.parse
import folium

def update_df():
    dotenv.load_dotenv()
    KEY = os.getenv('TWITTER_API_KEY')
    SECRET = os.getenv('TWITTER_API_KEY_SECRET')

    # Connect to the Twitter API        
    TWITTER_AUTH = tweepy.OAuthHandler(KEY, SECRET)
    TWITTER = tweepy.API(TWITTER_AUTH)

    auth = tweepy.OAuthHandler(KEY, SECRET)
    
    # set access to user's access key and access secret 
    
    # calling the api 
    
    api = tweepy.API(auth)

    user = api.get_user(screen_name='pdxpolicelog')

    tweets = user.timeline(
            count=2000,
            exclude_replies=True,
            include_rts=False,
            tweet_mode="extended",
        )

    tweets_and_dates = []
    for pages in tweepy.Cursor(api.user_timeline,screen_name='pdxpolicelog').items(3):
        #print(pages)
        tweets_and_dates.append(pages.text + ", " + str(pages.created_at))
        
    df = pd.DataFrame({'tweets' : tweets_and_dates})

    for i in df['tweets']:
        df['split'] = df['tweets'].apply(lambda x: x.rpartition("at"))
    
    categories = []

    for i in range(0, len(df['split'])):
        category = df['split'][i][0]
        categories.append(category)
    df['category'] = categories

    dates = []
    for i in range(0, len(df['split'])):
        date = df['split'][i][2]
        dates.append(date)
    df['dates'] = dates

    for i in df['dates']:
        df['datesplit'] = df['dates'].apply(lambda x: x.rpartition(","))
    
    datesplit = []
    for i in range(0, len(df['split'])):
        datesp = df['datesplit'][i][0]
        datesplit.append(datesp)
    df['datessplit2'] = datesplit

    tests = []
    for i in range(0, len(df['datessplit2'])):
        test = df['datessplit2'][i].split(',')
        tests.append(test)

    df['formatted'] = tests

    addresses = []
    for i in range(0, len(df['datessplit2'])):
        real_addresses = df['formatted'][i][0]
        addresses.append(real_addresses)

    df['address'] = addresses

    for i in df['tweets']:
        df['datestest'] = df['tweets'].apply(lambda x: x.rpartition("#pdx911,"))


    dates = []
    for i in range(0, len(df['datestest'])):
        date = df['datestest'][i]
        date = date[2]
        dates.append(date)
    df['dates'] = dates

    df = df.drop(columns=['split', 'formatted', 'datestest', 'datessplit2', 'datesplit'])

    df['newaddress'] = df['address'] + ", Portland, OR"

    addresses = []
    for i in range(0, len(df['newaddress'])):
        addy = df['newaddress'][i]
        addresses.append(addy)

    lattitude = []
    longitude = []
    coordinates = []
    for i in range(0, len(df['newaddress'])):
        try:
            url = 'https://nominatim.openstreetmap.org/search/' + urllib.parse.quote(addresses[i]) +'?format=json'
            response = requests.get(url).json()
            print(response[0]["lat"])
            print(response[0]["lon"])
            lat_reply = response[0]["lat"]
            long_reply = response[0]["lon"]
            lattitude.append(lat_reply)
            longitude.append(long_reply)
            coordinate = str(long_reply) + ", " + str(lat_reply)
            coordinates.append(coordinate)
        except IndexError:
            lat_reply = 0
            long_reply = 0
            lattitude.append(lat_reply)
            longitude.append(long_reply)
            coordinate = str(long_reply) + ", " + str(lat_reply)
            coordinates.append(coordinate)

    df['lattitude'] = lattitude
    df['longitude'] = longitude
    df['coordinates'] = coordinates

    for i in range(0, len(df['coordinates'])):
        df['newcoordinates']= df['coordinates'].apply(lambda x: tuple(map(float, x.split(', '))))

    df.replace(0,np.nan).dropna(axis=1,how="all", inplace=True)
    df_filtered = df[df['lattitude'] != 0]
    df = df_filtered
    df = df.reset_index()
    return df

def add_markers_to_the_map(my_map, df, color, icon):  
    points = list(zip(df.newcoordinates, df.category, df.address, df.dates))
    for point in points:         
            popup_text = "{}, {}, {}".format(point[1], str(point[2]), point[3])
        
            popup = folium.Popup(popup_text, autopan='False', parse_html=True, max_width=500)
                
            marker = folium.Marker(location=[point[0][1], point[0][0]], 
                                   popup=popup, 
                                   icon = folium.Icon(icon_size=(18, 24), color=color, icon=icon, prefix='fa')).add_to(my_map)
    return my_map