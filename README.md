# amazon_lead_generator
a simple tool used to pull product data and filter it by brand registered status 

## Context
I run a brand management company for small businesses on Amazon. Essentially we help them control their sales channel on Amazon by updating their listtings, removing unwanted 3rd parties, implementing price control, updating listings, launching new products etc. 

## Problem
Finding new clients is laborious. I have 2 VAs browsing Amazon looking for products with unoptimzed listings with zero brand registry, and then cold email them. This is time consuming. Keepa API has a product finder library that allows me to create custom queries, but one thing was always missing: Brand Registry status. The companies we want to work with are primarily not brand registered, but there is no feature in the keepa or Amazon developers API that would indicate if the brand for the product listing is brand registered. You can easily tell by visiting the Amazon product page by looking for the "Visit the Brand Storefront" under the product title, but doing that manually is a pain. 

## Method
I use Keepa API to load a custom product query then use scrapeops to scrape the ASIN pages looking for the brand storefront, then filter out those results. I have not optimzed this code in the slightest and the runtime is about 5 minutes depending on how many products I request but it sure beats the weeks time it usually takes to build a lead list by hand. Now it runs daily on a schedule. Previously we would build a lead least of 100 leads a week and maybe only about half of them we usable. Now I can generate the same amount of leads of the same quality in about 5 minutes where it previously took a week. Cold emailing still sucks though. I've begun some basic CRM integration, will add when I deem it cost effective. 

## Deployment
Current implementation is a flask app. I plan to deploy it in the future for my VAs to use. 
