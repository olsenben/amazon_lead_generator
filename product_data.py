import requests
import urllib.parse
import json
from tqdm import tqdm


class KeepaAPI():
    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self,query_params):
        """runs api requests and returns response in json string format"""
        
        asins = self.request_asins(query_params)
        asin_dict = {}

        if asins:
            for item in tqdm(asins['asinList'],desc='Requesting Asin Data'):
                product = self.request_asin_data(item)
                product_data = product['products'][0]
                
                #filter brand registered
                if 'brandStoreName' in product_data:
                    continue
                else:
                    asin_dict[item] ={}
                    asin_dict[item]['brand'] = product_data['brand']
                    asin_dict[item]['url'] = "https://www.amazon.com/dp/" + item
            
            return asin_dict
        else:
            print("Data request unsuccessful")
            return None


    def request_asins(self, query_params, domain_id=1):
        """fetches list of ASINS according to parameters (json string formatting)"""

        query_json = urllib.parse.quote(json.dumps(query_params))

        api_endpoint = f'https://api.keepa.com/query?key={self.api_key}&domain={domain_id}&selection={query_json}'

        response = requests.get(api_endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            print("Asin request unsuccessful")
            print(f"Error: {response.status_code}")
            return None
        
    def request_asin_data(self, asin, domain_id=1):
        """queries product data for specific data"""

        api_endpoint = f'https://api.keepa.com/product?key={self.api_key}&domain={domain_id}&asin={asin}'

        response = requests.get(api_endpoint)

        if response.status_code == 200:
            return response.json()
        else:
            print("ASIN data request unsuccessful")
            print(f"Error: {response.status_code}")
            return None
        
def load_query_parameters(QUERY_PATH):
    try:     
        with open(QUERY_PATH, 'r') as file:
            return json.load(file)
    except:
        print('Error Loading Query Parameters File')
        return None


def run_request(keepa_api_key, query_parameters):
    keepa = KeepaAPI(keepa_api_key)

    parsed_asins = keepa.get_data(query_parameters)

    return parsed_asins








        
        

