import unicodedata
import re
import json

import nltk
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.corpus import stopwords

import pandas as pd
from sklearn.model_selection import train_test_split

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

    return tokenizer.tokenize(article, return_str=True)

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

    # print('Removed {} stopwords'.format(len(words) - len(filtered_words)))

    article_without_stopwords = ' '.join(filtered_words)
    
    return article_without_stopwords

def prepare_df(df, extra_words = [], exclude_words = []):
    """Adds columns for cleaned, stemmed, and lemmatized data in dataframe """
    # Create cleaned data column of content
    df['clean'] = df.original.apply(basic_clean).apply(tokenize).apply(remove_stopwords,
                                                       extra_words = extra_words,
                                                       exclude_words = exclude_words)
    
    # Create stemmed column with stemmed version of cleaned data
    df['stemmed'] = df.clean.apply(tokenize).apply(stem).apply(remove_stopwords,
                                                       extra_words = extra_words,
                                                       exclude_words = exclude_words)

    # Create lemmatized column with lemmatized version of cleaned data
    df['lemmatized'] = df.clean.apply(tokenize).apply(lemmatize).apply(remove_stopwords,
                                                       extra_words = extra_words,
                                                       exclude_words = exclude_words)
    
    return df
    
    
def create_prepared_news_df(extra_words =[], exclude_words = []):
    """Run this function to generate a prepared news article dataframe with cleaned, stemmed, and lemmatized data"""
    news_df = pd.DataFrame(acquire.get_news_articles())
    
    return prepare_df(news_df, extra_words, exclude_words)
    
def create_prepared_blog_df(extra_words =[], exclude_words = []):
    """Run this function to generate a prepared Codeup Blog dataframe with cleaned, stemmed, and lemmatized data"""

    codeup_df = pd.DataFrame(acquire.get_blog_articles())
    
    return prepare_df(codeup_df, extra_words, exclude_words)
    
    
def train_validate_test_split(df, target, seed=123):
    '''
    This function takes in a dataframe, the name of the target variable
    (for stratification purposes), and an integer for a setting a seed
    and splits the data into train, validate and test. 
    Test is 20% of the original dataset, validate is .30*.80= 24% of the 
    original dataset, and train is .70*.80= 56% of the original dataset. 
    The function returns, in this order, train, validate and test dataframes. 
    '''
    train_validate, test = train_test_split(df, test_size=0.2, 
                                            random_state=seed, 
                                            stratify=df[target])
    train, validate = train_test_split(train_validate, test_size=0.3, 
                                       random_state=seed,
                                       stratify=train_validate[target])
    return train, validate, test