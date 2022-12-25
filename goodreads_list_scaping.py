import requests 
from bs4 import BeautifulSoup
import pandas as pd
import html5lib
import os

path = os.getcwd()

gr_list_page = r"https://www.goodreads.com/list/show/1.Best_Books_Ever?page="
list_of_lists = [gr_list_page + str(i) for i in range(1,3)]

def book_title_links(url):
    
    def get_soup(url):
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        return soup

    def all_href_tag_class(soup, h_tag, h_class, append=''):
        value = soup.find_all(h_tag, class_=h_class)
        href_list = [append + i.get('href') for i in value]
        return href_list
    
    soup = get_soup(url)
    links = all_href_tag_class(soup, 'a', 'bookTitle',
                               'https://www.goodreads.com')
     
    return links


books_links = []
for i in list_of_lists:
    for j in book_title_links(i):
        books_links.append(j)
links_series = pd.Series(books_links)
links_series.to_csv(path+r"\data\books_links_test.csv", index=False)

