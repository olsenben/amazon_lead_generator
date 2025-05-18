import requests
import urllib.parse
import json
from tqdm import tqdm
import os
from datetime import datetime 


class KeepaAPI():
    """class to handle api requests from keepa"""
    def __init__(self, api_key):
        self.api_key = api_key

    def get_data(self,query_params, filter_seen_brands=True, filter_br=True):

        """runs api requests and returns response in json string format
            parameter filter_br filters out brand registered asins if True
        """
        if filter_seen_brands:
            seen_brands_removed_params = self.filter_seen_brands(query_params, file_name="brands_record.json", dir="data")
            asins = self.request_asins(seen_brands_removed_params)
        else:
            asins = self.request_asins(query_params)

        if asins:
            asin_list = asins['asinList']
            filtered_br_asins = self.filter_brand_registered(asin_list, on=filter_br)
            self.log_brands(data_dict=filtered_br_asins)
            return filtered_br_asins
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
        
    def filter_brand_registered(self, asin_list, on=True):
        """ 
        request product info for list of asins, checks if they are brand registered,
        returns dict of asins with page link and manufacturer
        """
        asin_dict = {}

        for item in tqdm(asin_list,desc='Requesting Asin Data'):
                product = self.request_asin_data(item)
                product_data = product['products'][0]
                
                #filter brand registered
                if on:    
                    if 'brandStoreName' in product_data:
                        continue
                    else:
                        asin_dict[item] ={}
                        asin_dict[item]['manufacturer'] = product_data.get('manufacturer') or product_data.get('brand')
                        asin_dict[item]['url'] = "https://www.amazon.com/dp/" + item
                else:
                    asin_dict[item] ={}
                    asin_dict[item]['manufacturer'] = product_data.get('manufacturer') or product_data.get('brand')
                    asin_dict[item]['url'] = "https://www.amazon.com/dp/" + item
            
        return asin_dict
    
    def filter_seen_asins(self, asin_list, file_name="asins_record.json", dir="data"):
        """filters asin list and removes Asins that have already been seen"""
        
        old_asins = load_json(file_name,dir)
        time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

        #if no records exist, create new records and return original list
        if old_asins is None:
            print("No Asin Records Found!")
            print("Starting new records...")
            new_asin_dict = {}
            new_asin_dict[time] = asin_list
            save_to_json(new_asin_dict,file_name,dir)
            return asin_list
        
        #filter list
        else:
            print("Asin records loaded")
            seen_asins = set()
            for value in old_asins.values():
                if isinstance(value, list):
                    seen_asins.update(value)
                else:
                    seen_asins.add(value)
            filtered_list = []
            for asin in asin_list:
                if asin not in seen_asins:
                    filtered_list.append(asin)
                    seen_asins.add(asin)

            #save new record to json
            old_asins[time] = list(seen_asins)
            file_path = os.path.join(dir, file_name)
            with open(file_path, "w") as file:
                json.dump(old_asins, file, indent=4)
            print("data saved")

            return filtered_list

    def log_brands(self, data_dict,file_name="brands_record.json", dir="data"):
        """logs seen brand"""

        brand_log = load_json(file_name,dir)
        time = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        dict_brands = [i['manufacturer'] for i in data_dict.values()]


        #if no records exist, create new records and save latest dictionary
        if brand_log is None:
            print("No brand Records Found!")
            print("Starting new records...")
            new_brand_dict = {}
            new_brand_dict[time] = list(set(dict_brands))
            save_to_json(new_brand_dict,file_name,dir)
        else:
            seen_brands = set()
            for value in brand_log.values():
                if isinstance(value, list):
                    seen_brands.update(value)
                else:
                    seen_brands.add(value)
            new_brands = [i for i in dict_brands if i not in seen_brands]

            #save new record to json
            brand_log[time] = list(set(new_brands))
            save_to_json(brand_log,file_name,dir)
            print("Brand log saved")


    def filter_seen_brands(self, query_params, file_name="brands_record.json", dir="data"):
        """modifies query parameters to avoid seen brands"""

        brand_log = load_json(file_name,dir)

        #if directory/file doesnt exist, create it
        if brand_log is None:
            print("No brand Records Found!")
            return query_params
        
        #modify paramaters with seen brands and pass those to search terms. 
        else:
            seen_brands = set()
            for value in brand_log.values():
                if isinstance(value, list):
                    seen_brands.update(value)
                else:
                    seen_brands.add(value)
            seen_brands = ["-" + i if i is not None else i for i in seen_brands ]
            new_query_params = query_params
            new_query_params['manufacturer'] = seen_brands
            return new_query_params
                
        
class ApolloAPI():
    """I built this whole part out for connecting to Apollos CRM API and then it turns out 
        free accounts have api access but dont get 99% of endpoints. thats what I get 
        for not reading the documentation closely enough. This code is here for when I decide
        the 60 bucks a month is worth while.
    """
    def __init__(self, api_key):
        self.api_key = api_key

    def request_data(self, url):
        """idk guess I'll hard code the header. 
        I think the header is the same no matter what, just the url is different
        """
        url = url

        headers = {
            "accept": "application/json",
            "Cache-Control": "no-cache",
            "Content-Type": "application/json",
            "x-api-key" : self.api_key
        }

        response = requests.post(url, headers=headers)

        if response.status_code == 200:
            return response.json()
        else:
            print("Apllo request unsuccessful")
            print(f"Error: {response.status_code}")
            return None
        
    def get_companies(self, parsed_asins):
        """request company info for manufacturer. must be preparsed by KeepaAPI method get_data()"""

        base_url = "https://api.apollo.io/api/v1/mixed_companies/search?organization_ids[]="
        
        print("Requesting company data")

        products = parsed_asins

        for asin, data in products.items():
            manufacturer_name = data['manufacturer']
            url = urllib.parse.quote(base_url + manufacturer_name)
            data = self.request_data(url)
            products[asin]['company'] = data

        return products

def load_json(filename, dir_name="data"):
    try:
        file_path = os.path.join(dir_name, filename)     
        with open(file_path, 'r') as file:
            return json.load(file)
    except:
        print(f'Error Loading {filename}')
        return None

def save_to_json(json_string, filename, dir_name="data"):
    
    data_dir = dir_name

    if not os.path.exists(data_dir):
        os.makedirs(data_dir)    

    path = os.path.join(dir_name,filename)
    
    with open(path, "w", encoding='utf-8') as file:
        json.dump(json_string, file, indent=4)

    print("data saved")


def run_request(keepa_api_key, query_parameters):
    keepa = KeepaAPI(keepa_api_key)

    parsed_asins = keepa.get_data(query_parameters)

    return parsed_asins


# if __name__ == "__main__":
#     api_key = '3pl62cnd2u9i76h5nkd0jlrls8k8j0007dnssmf7usf8b4m6soh41omqnljbojvl'

#     keepa = KeepaAPI(api_key)
#     cache_path = 'cached_results.json'
#     query = load_json('query_parameters.json')
#     print()
#     products = keepa.get_data(query, filter_seen_brands=True)
#     print(products)






        
        

