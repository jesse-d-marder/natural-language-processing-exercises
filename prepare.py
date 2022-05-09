import unicodedata
import re
import json

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords

import pandas as pd

import acquire

def basic_clean(article:str):
    """ Performs basic cleaning of text string, article, by switching all letters to lowecase, normalizing unicode characters, 
    and replacing everything that is not a letter, number, whitespace, or single quote."""
    # Convert text to lowercase
    article = article.lower()
    
    # Remove accented characteries. Normalize removes inconsistencies in unicode character encoding.
    # Encode converts string to ASCII and decode returns the bytes into string.
    article = unicodedata.normalize('NFKD', article)\
    .encode('ascii', 'ignore')\
    .decode('utf-8', 'ignore')

    # remove anything that is not a through z, a number, a single quote, or whitespace
    article = re.sub(r"[^a-z0-9'\s]", '', article)
    
    return article

def tokenize(article:str):
    """ Takes in a string, article, and tokenizes all words """
    
    tokenizer = nltk.tokenize.ToktokTokenizer()

    return tokenizer.tokenize(original, return_str=True)

def stem(article: str):
    """ Takes in a string, article, and returns text after applying stemming using Porter method """
    
    ps = nltk.porter.PorterStemmer()

    stems = [ps.stem(word) for word in article.split()]
    article_stemmed = ' '.join(stems)
    
    return article_stemmed

def lemmatize(article: str):
    """ Accepts string as argument, article, and returns text after applying lemmatization to each word """
    
    wnl = nltk.stem.WordNetLemmatizer()
        
    lemmas = [wnl.lemmatize(word) for word in article.split()]
    article_lemmatized = ' '.join(lemmas)

    return article_lemmatized

def remove_stopwords(article: str, extra_words: list, exclude_words: list):
    """ Accepts string (article) as argument and returns text after removing all the stopwords.
    extra_words: any additional stop words to include (these words will be removed from the article)
    exclude_words: any words we do not want to remove. These words are removed from the stopwords list and will remain in article """
    
    stopword_list = stopwords.words('english')

    [stopword_list.append(word_to_add) for word_to_add in extra_words if word_to_add not in stopword_list]
    [stopword_list.remove(to_remove) for to_remove in exclude_words if to_remove in stopword_list]

    words = article.split()
    filtered_words = [w for w in words if w not in stopword_list]

    print('Removed {} stopwords'.format(len(words) - len(filtered_words)))

    article_without_stopwords = ' '.join(filtered_words)
    
    return article_without_stopwords

def prepare_df(df):
    
    # Create cleaned data column of content
    df['clean'] = df.apply(lambda row: basic_clean(row.original), axis=1)
    
    # Create stemmed column with stemmed version of cleaned data
    df['stemmed'] = df.apply(lambda row: stem(row.clean), axis=1)

    # Create lemmatized column with lemmatized version of cleaned data
    df['lemmatized'] = df.apply(lambda row: lemmatize(row.clean), axis=1)
    
    return df
    
    
def create_prepared_news_df():
    
    news_df = pd.DataFrame(acquire.get_news_articles())
    
    return prepare_df(news_df)
    
def create_prepared_blog_df():
    
    codeup_df = pd.DataFrame(acquire.get_blog_articles())
    
    return prepare_df(codeup_df)
    
    
