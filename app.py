from flask import Flask, render_template, url_for, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import pandas as pd
import json
from lead_scraper_script import run_request


load_dotenv()

#load api keys
keepa_api_key= os.getenv("KEEPA_API_KEY")
scrapeops_api_key = os.getenv("SCRAPEOPS_API_KEY")
scrapeops_url = 'https://proxy.scrapeops.io/v1/'

app = Flask(__name__)
CACHE_PATH = "cached_results.json"
QUERY_PATH = 'query_parameters.json'

def load_query_parameters():
    try:     
        with open(QUERY_PATH, 'r') as file:
            return json.load(file)
    except:
        print('Error Loading Query Parameters File')
        return None
    
def fetch_and_cache_data():
    print("Refreshing...")
    query_parameters = load_query_parameters()
    df = run_request(keepa_api_key, query_parameters, scrapeops_api_key, scrapeops_url)
    df.to_json(CACHE_PATH, orient='records', indent=4)
    print("Parsing complete")

@app.route('/')
def index():
    if os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r") as file:
            products = json.load(file)
    else:
        products = []
    return render_template('index.html', products=products)

@app.route('/refresh')
def refresh():    
    fetch_and_cache_data()
    return redirect(url_for('index'))


#refresh results once a day
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_cache_data, trigger='interval', hours=24)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)