import json
import os

import requests
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium import webdriver


# Replace 'YOUR_API_KEY' with your actual NYT API key
api_key = 'Wwx6bZPiGGZtwHVO2ArVmcTbslnRGhR8'
api_url = 'http://api.nytimes.com/svc/news/v3/content/all/business.json'
# Set up the parameters, including the API key
params = {'api-key': api_key}
# Make the GET request
response = requests.get(api_url, params=params)
# Writing to sample.json]
open('data.json', 'w').close()
with open('data.json', 'w') as fp:
    json.dump(response.json(), fp)

def getHTML(url):
    apikey = '832c45ed810d72e73f4950140817d64af4a7d44d'
    params = {
        'url': url,
        'apikey': apikey,
        'js_render': 'true',
    }
    return requests.get('https://api.zenrows.com/v1/', params=params).text

def parseHTML(html):
    soup = BeautifulSoup(html, features='html.parser')

    return soup.get_text()


# Check if the request was successful (status code 200)
if response.status_code == 200:
    # Parse and summarize artilces of interest
    data = response.json()
    url = ''
    
    # TODO: pick best articles
    for i in range(data["num_results"]):
        article = data["results"][i]
        if article["subsection"] == "Economy":
            url = article['url']
            break

    print(url)

    print(parseHTML(getHTML(url)))
    # summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
    
# Error handling
else:
    print(f"Error: {response.status_code}")
    print(response.text)