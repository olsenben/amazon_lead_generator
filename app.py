from flask import Flask, render_template, url_for, redirect
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import json
from product_data import run_request, load_json, save_to_json

#next steps:
#add a way to hide asins
#maybe add pagination
#add brand info via apollo api
#add download to csv button
#deploy (maybe add credentialing?)

load_dotenv()

#load api keys
keepa_api_key= os.getenv("KEEPA_API_KEY")
# scrapeops_api_key = os.getenv("SCRAPEOPS_API_KEY")
# scrapeops_url = 'https://proxy.scrapeops.io/v1/'

app = Flask(__name__)
CACHE_PATH = "cached_results.json"
QUERY_PATH = 'query_parameters.json'

def get_min_products(keepa_api_key, query_parameters, min_products=15):
    """runs get_data until minimum number of filtered products are gathered"""
    query_parameters = query_parameters
    query_parameters['page'] = 1
    data = run_request(keepa_api_key, query_parameters)
    while len(data.keys()) < min_products:
        query_parameters['page'] += 1
        more_data = run_request(keepa_api_key, query_parameters)
        data.update(more_data)
    
    return data

def fetch_and_cache_data():
    """fetches products and the caches the results"""
    print("Refreshing...")
    query_parameters = load_json(QUERY_PATH)
    data = get_min_products(keepa_api_key, query_parameters)
    save_to_json(data, CACHE_PATH)
    print("Parsing complete")


@app.route('/')
def index():
    """loads cached products and renders html template"""
    print("Loading Cache...")
    products = load_json(CACHE_PATH)
    if products is None:
        products = {}
        return render_template('index.html', products=products)
    else:
        return render_template('index.html', products=products)

@app.route('/refresh')
def refresh(): 
    """button to refresh results"""   
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