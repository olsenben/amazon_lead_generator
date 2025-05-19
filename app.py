from flask import Flask, render_template, url_for, redirect, send_file, make_response
from apscheduler.schedulers.background import BackgroundScheduler
from dotenv import load_dotenv
import os
import json
from product_data import run_request, load_json, save_to_json
import csv
import io

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

@app.route('/download_csv')
def download_csv():
    """Reads the cached JSON and returns a CSV file."""
    products = load_json(CACHE_PATH)
    if not products:
        return "No data available", 404

    #prepare csv in-memory
    output = io.StringIO()
    writer = csv.DictWriter(output, fieldnames=["asin", "manufacturer", "url"])
    writer.writeheader()

    for asin, details in products.items():
        row = {"asin": asin, **details}
        writer.writerow(row)

    #create Flask response
    response = make_response(output.getvalue())
    response.headers["Content-Disposition"] = "attachment; filename=products.csv"
    response.headers["Content-type"] = "text/csv"
    return response


#refresh results once a day
scheduler = BackgroundScheduler()
scheduler.add_job(func=fetch_and_cache_data, trigger='interval', hours=24)
scheduler.start()

import atexit
atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)