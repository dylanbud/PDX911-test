import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import flask
import tweepy
from os import getenv
from flask import Flask, render_template, request
from werkzeug.datastructures import UpdateDictMixin
from .query import *
import folium

def create_app():
    # initializes our app
    app = Flask(__name__)

    # Listen to a "route"
    # '/' is the home page route
    @app.route('/')
    def index():
        start_coords = (45.514811, -122.679109)
        folium_map = folium.Map(location=start_coords, zoom_start=14)
        return folium_map._repr_html_()

    @app.route('/update')
    def update():
        '''update the map'''
        df = update_df()
        start_coords = (45.514811, -122.679109)
        folium_map = folium.Map(location=start_coords, zoom_start=14)
        add_markers_to_the_map(folium_map, df, color = 'red', icon='info')
        return folium_map._repr_html_()
    
    # API ENDPOINTS (Querying and manipulating data in a database)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        # request.values is pulling data from the html
        # use the username from the URL (route)
        # or grab it from the dropdown menu
        name = name or request.values['user_name']

        #If the user exists in the db already, update it, and query for it
        
        try:
            if request.method == 'POST':
                add_or_update_user(name)
                message = f"User {name} Successfully Added!"

            #From the user that was just added / Updated 
            # get their tweets to display on the /user/<name> page
            tweets = User.query.filter(User.username == name).one().tweets

        except Exception as e:
            message = f"Error adding {name}: {e}"

            tweets = []

        return render_template('user.html', title=name, tweets=tweets, message=message)


    @app.route('/compare', methods=['POST'])
    def compare():
        user0 , user1 = sorted([request.values['user0'], request.values['user1']])

        if user0 == user1:
            message = "Cannot compare users to themselves!"

        else:
            prediction = predict_user(user0, user1, request.values['tweet_text'])
            if prediction == 0:
                predicted_user = user0
                non_predicted_user = user1
            else:
                predicted_user = user1
                non_predicted_user = user0
            message = f"'{request.values['tweet_text']}' is more likely to be said by '{predicted_user}' than by '{non_predicted_user}'"

        return render_template('prediction.html', title='Prediction', message=message)
        
    return app