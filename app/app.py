import numpy as np
import pandas as pd
import flask
import tweepy
from os import getenv
from flask import Flask, render_template, request
from werkzeug.datastructures import UpdateDictMixin
import folium
from app.query import initialize_df
from query import update_df, add_markers_to_the_map, more_markers
import sqlite3

def create_app():
    # initializes our app
    app = Flask(__name__)

    # Listen to a "route"
    # '/' is the home page route
    @app.route('/')
    def index():
        start_coords = (45.514811, -122.679109)
        folium_map = folium.Map(location=start_coords, zoom_start=14)
        df_pdx = initialize_df()
        return folium_map._repr_html_()

    @app.route('/update')
    def update():
        '''update the map'''
        #df = update_df()
        df_pdx = initialize_df()
        start_coords = (45.514811, -122.679109)
        folium_map = folium.Map(location=start_coords, zoom_start=14)
        more_markers(folium_map, df_pdx, color = 'red', icon='info')
        return folium_map._repr_html_()
        
    return app

