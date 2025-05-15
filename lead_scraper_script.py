import requests
import urllib.parse
import json
import pandas as pd
#import random
from bs4 import BeautifulSoup
from tqdm import tqdm
import os
from datetime import datetime

class KeepaAPI():
    def __init__(self, api_key):
        self.api_key = api_key

    def get_asins(self, query_params, domain_id=1):
        """fetches list of ASINS according to parameters (json string formatting)"""

        query_json = urllib.parse.quote(json.dumps(query_params))

        api_endpoint = f'https://api.keepa.com/query?key={self.api_key}&domain={domain_id}&selection={query_json}'

        response = requests.get(api_endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: {response.status_code}")
            return None
        
class AsinParser():
    def __init__(self, api_key, url):
        self.api_key = api_key
        self.url = url

    def parse_asins(self, response_data):
        """parse list of asins by brand registered status"""

        df = self.create_df(response_data)

        filtered_df = self.filter_by_br(df)

        return filtered_df


    def create_df(self, response_data):
        """create df from retrieved data"""

        
        df= pd.DataFrame(response_data['asinList'], columns=['asinList'])

        df['asinLink'] = df['asinList'].apply(lambda x: "https://www.amazon.com/dp/" + x)
        return df
    
    def is_brand_registered(self, asin_url):
        """checks link and returns True if product is brand registered, False otherwise"""

        try:
            #fetch the HTML content of the product page with scrapeops proxy
            response = requests.get(
                url = self.url,
                params = {
                    'api_key' : self.api_key,
                    'url' : asin_url,
                },
                timeout=15  # Set timeout to avoid hanging requests
            )
            #store html retrieved by scrapeops
            soup = BeautifulSoup(response.content, 'html.parser')

            # Check for the presence of "visit the [brand name] store" text by element tag <a>, id "bylineInfo", class "a-link-normal"
            store_text = soup.find("a", {"id": "bylineInfo", "class": "a-link-normal"}, string=lambda text: text and "Visit the " in text and " Store" in text)
            return bool(store_text)
    
        except requests.exceptions.RequestException as e:
            print(f"Request error for {asin_url}: {e}")
        except Exception as e:
            print(f"Error fetching or parsing page {asin_url}: {e}")
        
        return False
    
    def filter_by_br(self, df):
        """removes asins by with brand registered status"""
        
        tqdm.pandas(desc="Checking brand registration")

        filtered_asins = df[~df['asinLink'].progress_apply(self.is_brand_registered)]

        return filtered_asins
    
def run_request(keepa_api_key, query_parameters, scrapeops_api_key, scrapeops_url):
    keepa = KeepaAPI(keepa_api_key)
    parser = AsinParser(scrapeops_api_key, scrapeops_url)

    response_data = keepa.get_asins(query_parameters)

    parsed_asins = parser.parse_asins(response_data)

    return parsed_asins


        



