import pandas as pd
import numpy as np
from requests import get
from bs4 import BeautifulSoup
import os

def get_post_details(post):
    """ Returns dictionary of url, title, date published, and content for each post on the Codeup.com/blog site"""
    output = {}
    # Extract URL
    output['url'] = post.select('a')[0].attrs['href']
    # Extract title
    output['title'] = post.text.strip()
    # Extract date published
    output['date_published'] = post.select('span.published')[0].text
    # Extracts blog post contents
    output['content'] = get_blog_content(output['url'])
    
    return output

def get_blog_content(url):
    """ Returns the content of the blog post """
    headers = {'User-Agent': 'Codeup Data Science'} # Some websites don't accept the pyhon-requests default user-agent
    response = get(url, headers=headers)


    # Make a soup variable holding the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    entry_text = ""
    for t in soup.select('div.entry-content'):
        entry_text += t.text.strip()
    return entry_text

def get_blog_articles(return_dataframe = False):
    """ Returns dictionary (or dataframe) of information about blog posts on codeup.com/blog site """
    url = 'https://codeup.com/blog/'
    headers = {'User-Agent': 'Codeup Data Science'} # Some websites don't accept the pyhon-requests default user-agent
    response = get(url, headers=headers)


    # Make a soup variable holding the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    if return_dataframe:
        return pd.DataFrame([get_post_details(post) for post in soup.select('article.et_pb_post')])

    return [get_post_details(post) for post in soup.select('article.et_pb_post')]

def get_category_news_cards(category):
    """ Returns list with each item the soup for a different news card from the category page"""
    
    # Note that having the category name capitalized sends you to a different website than lowercase!!
    base_url = r'https://inshorts.com/en/read'
    url = base_url +r'/'+category.lower()
    
    headers = {'User-Agent': 'Codeup Data Science'} # Some websites don't accept the pyhon-requests default user-agent
    response = get(url, headers=headers)

    # Make a soup variable holding the response content
    cat_soup = BeautifulSoup(response.content, 'html.parser')
    
    return cat_soup.select('div.news-card.z-depth-1')

def get_news_details(news_card, category):
    """ Returns dictionary with information about the article 
    news_card: the soup for an individual news card within a category card stack
    category: this is passed to this function so it can be inputted to the dictionary"""
    
    output={}
    output['headline'] = news_card.select('div.news-card-title')[0].find("span").text
    output['author'] =  news_card.select('div.news-card-author-time')[0].find('span', class_='author').text
    output['datetime'] = news_card.select('div.news-card-author-time')[0].find('span', class_='time').attrs['content']
    output['category'] = category.lower()
    output['content'] = news_card.select('div.news-card-content')[0].find('div').text
    
    return output
    
def get_each_news_in_category(category):
    """ Returns list of dictionaries for each article in the category with article information """
    if category == 'india':
        category = 'national'
    list_of_news_cards = get_category_news_cards(category)
    print("Total News Articles in Category: ",len(list_of_news_cards))
    return [get_news_details(news_card, category) for news_card in list_of_news_cards]
    
def get_news_categories(soup):
    """ Returns list of news categories from the inshorts homepage """
    
    categories = soup.select('ul.category-list')[0].select('li.active-category')[1:]
    
    return [c.text.lower() for c in categories]

def get_news_articles(desired_categories = 'all', get_fresh_news = False):
    """ Returns dictionary of news article information from https://inshorts.com/ .
    desired_categories: 'all' by default or a list of categories desired
    update_cache: if True gets fresh news"""
    
    # Filepath for cache
    news_cache_file = 'news.csv'
    
    if not get_fresh_news:
        if os.path.exists(news_cache_file):
            print("Importing from csv")
            return pd.read_csv('news.csv')
        else:
            print("News cache does not exist, acquiring fresh news...")
            # Condition when don't want fresh news but no cache exists, ensure new data is cached to csv
            need_cache = True
    
    
    url = 'https://inshorts.com/en/read'
    headers = {'User-Agent': 'Codeup Data Science'} # Some websites don't accept the python-requests default user-agent
    response = get(url, headers=headers)


    # Make a soup variable holding the response content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    categories = get_news_categories(soup)
    
    # Initialize news list
    news = []
    
    # Check if we want articles from all categories or just specific ones
    if desired_categories == 'all':
        
        # Iterate through each category, scraping each article, save details to news list
        for cat in categories:
            
            print("Scraping category: ", cat)
            news+=get_each_news_in_category(cat)
    else:
        # For the case when we only want to scrape articles in particular categories
        for cat in desired_categories:
            # Checks if the desired category exists. If it doesn't moves on to the next category desired
            if cat.lower() not in categories:
                print(cat,"does not exist at site, skipping this category")
                continue
            print("Scraping category: ", cat)
            news+=get_each_news_in_category(cat)
    
    # Write results to cache
    if get_fresh_news or need_cache:
        pd.DataFrame(news).to_csv(news_cache_file, index = None)
       
    return news