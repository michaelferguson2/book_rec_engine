from bs4 import BeautifulSoup
import lxml
import pandas as pd
import re
from selenium.webdriver import Chrome
import time
import numpy as np
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import os
import datetime 

#alaska = r"https://www.goodreads.com/book/show/99561.Looking_for_Alaska"
#potter = r"https://www.goodreads.com/book/show/72193.Harry_Potter_and_the_Philosopher_s_Stone"
#hunger = r"https://www.goodreads.com/book/show/2767052-the-hunger-games"

def get_soup_wd(url):
    driver.get(url)
    content = driver.page_source
    soup = BeautifulSoup(content, 'lxml')
    return soup


def get_title_wd(soup):
    old_site_check = soup.find(id="bookTitle")
    new_site_check = soup.find(attrs={"class":"BookPageTitleSection__title"})

    if old_site_check != None:
        title = soup.find(id="bookTitle").get_text(strip=True)
    elif new_site_check != None:
        title = soup.find(attrs={"data-testid":"bookTitle"}).get_text(strip=True)
    else:
        title = np.nan
    return title
 
   
def get_genre_wd(soup):
    genres = []
    for i in soup.find_all("span", {"class":"BookPageMetadataSection__genreButton"}):
        genres.append(i.get_text(strip=True))
    if len(genres) == 0:
        for i in soup.find_all("a", {"class":"actionLinkLite bookPageGenreLink"}):
            genres.append(i.get_text(strip=True))             
    return genres


def get_author_wd(soup):
    old_site_check = soup.find("a", {"class":"authorName"})
    new_site_check = soup.find("span", {"class":"Formatted"})

    if old_site_check != None:
        author = soup.find("a", {"class":"authorName"}).text
    elif new_site_check != None:
        author = soup.find("span", {"class":"ContributorLink__name"}).text
    else:
        author = np.nan
    return author      


def get_page_count_wd(soup):
    old_site_check = soup.find("span", {"itemprop":"numberOfPages"})
    new_site_check = soup.find("div", {"class":"FeaturedDetails"})

    if old_site_check != None:
        count = soup.find("span", {"itemprop":"numberOfPages"}).text
    elif new_site_check != None:
        count = soup.find("div", {"class":"FeaturedDetails"}).get_text(strip=True)[0:9]
    else:
        count = np.nan
    return count       


def get_publish_date_wd(soup):
    old_site_check = soup.find("nobr", {"class":"greyText"})
    new_site_check = soup.find("p", {"data-testid":"publicationInfo"})

    if old_site_check != None:
        date = soup.find("nobr", {"class":"greyText"}).get_text(strip=True)
    elif new_site_check != None:
        date = soup.find("p", {"data-testid":"publicationInfo"}).get_text(strip=True)
    else:
        date = np.nan
    return date


def get_cover_link_wd(soup):
    old_site_check = soup.find("div", {"class":"editionCover"})
    new_site_check = soup.find("div", {"class":"BookCover__image"})

    if old_site_check != None:
        link = soup.find("div", {"class":"editionCover"}).img['src']
    elif new_site_check != None:
        link = soup.find("div", {"class":"BookCover__image"}).img['src']
    else:
        link = np.nan
    return link


def get_rating_wd(soup):  
    old_site_check = soup.find("span", {"itemprop":"ratingValue"})
    new_site_check = soup.find("div", {"class":"RatingStatistics__rating"})

    if old_site_check != None:
        rating = soup.find("span", {"itemprop":"ratingValue"}).get_text(strip=True)
    elif new_site_check != None:
        rating = soup.find("div", {"class":"RatingStatistics__rating"}).get_text(strip=True)
    else:
        rating = np.nan

    return rating   


def get_unique_id(url):
    num_id = re.findall("\d+", url)[0]
    return num_id
  

def get_desc_new(soup):
    d_html = soup.find("span", {"class":"Formatted"})
    for br in d_html:
        br.replace_with("#" + br.text)

    return d_html.get_text()


def get_desc_old(soup):
    d_soup = soup.find(id="description")
    if d_soup.find(attrs={"data-text-id":True}) != None:
        d_id = d_soup.find(attrs={"data-text-id":True}).get('data-text-id')
        d_html = d_soup.find("span", {"id":"freeText"+d_id})
    else:
        d_html = d_soup # if there is no data-text-id because the desc is short

    for br in d_html:
        br.replace_with("#" + br.text)
    
    return d_html.get_text()


def get_desc_wd(soup):
    
    old_site_check = soup.find(attrs={"data-text-id":True})
    new_site_check = soup.find("span", {"class":"Formatted"})

    if old_site_check != None:
        desc = get_desc_old(soup)
    elif new_site_check != None:
        desc = get_desc_new(soup)
    else:
        desc = np.nan
    return desc    


web_path = (ChromeDriverManager().install())
s = Service(web_path)
driver = Chrome(service=s)

path = os.getcwd()
books_list = pd.read_csv(path+r"\data\books_links.csv")
books_list = books_list['0']
books_list_1000 = books_list[0:10]


title=[]
desc=[]
genres =[]
author = []
cover_link =[]
rating = []
page_count = []
publish_date = []
unique_id = []

for i in books_list_1000:
    soup_test = get_soup_wd(i)
    
    title.append(get_title_wd(soup_test))
    desc.append(get_desc_wd(soup_test))
    genres.append(get_genre_wd(soup_test))
    author.append(get_author_wd(soup_test))
    cover_link.append(get_cover_link_wd(soup_test))
    rating.append(get_rating_wd(soup_test))
    page_count.append(get_page_count_wd(soup_test))
    publish_date.append(get_publish_date_wd(soup_test))
    unique_id.append(get_unique_id(i)) 
    time.sleep(2)
     
books_df = pd.DataFrame({
    'author':author,
    'title':title,
    'desc':desc,
    'genre':genres,
    'cover link':cover_link,
    'rating':rating,
    'page count':page_count,
    'publish date':publish_date,
    'book link':books_list_1000,
    'unique_id':unique_id})



timestamp = str(datetime.datetime.now())[0:19]
output_title = "{} {}".format("book_data", timestamp)

books_df.to_csv(r"{}{}".format(output_title, ".csv"), index=False)
books_df.to_pickle("{}{}{}".format("./", output_title, ".pkl")) 

books_df.to_csv('test')
















