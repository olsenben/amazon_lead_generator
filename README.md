# amazon_lead_generator
a simple tool used to pull product data and filter it by brand registered status 

## Context
I run a brand management company for small businesses on Amazon. Essentially we help them control their sales channel on Amazon by updating their listtings, removing unwanted 3rd parties, implementing price control, updating listings, launching new products etc. 

## Problem
Finding new clients is laborious. I have 2 VAs browsing Amazon looking for products with unoptimzed listings with zero brand registry, and then cold email them. This is time consuming. Keepa API has a product finder library that allows me to create custom queries, but one thing was always missing: Brand Registry status. The companies we want to work with are primarily not brand registered. You can easily tell if they are brand registered by visiting the Amazon product page by looking for the "Visit the Brand Storefront" under the product title, but doing that manually is a pain. Luckily, Keepa also saves the link to the brand storefront. Absence of that indicates lack of brand registry. 

## Method
I use Keepa API to load a custom product query. Each request logs previously seen before brands, and on the next request those are explicitly removed from the request to save API tokens. The resulting list of asins I request again at the product level and filter based on whether or not the product object contains a storefront url. Previously we would build a lead least of 100 leads a week and maybe only about half of them we usable. Now I can generate the same amount of leads of the same quality in about 5 minutes. Cold emailing still sucks though. I've begun some basic CRM integration, will add when I deem it cost effective. 

## Deployment
Current implementation is a flask app, deployed via render. 

## To Run Locally: 
Set up by cloning the repo and running ```pip install -r requirements.txt``` in your virtual environment. Run app.py and navigate to the port specified in your terminal by opening it in your internet browswer. Note: you will need a keepa API key, saved in your ```.env``` like this:  ```KEEPA_API_KEY=your_key_here_no_parenthesis```
