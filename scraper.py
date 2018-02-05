# app store scraper

import requests
from bs4 import BeautifulSoup
from user_agent import generate_user_agent
import csv
import time
import threading
import random

# functions #
def site_open(site):

    '''get that beautiful soup'''

    try:
        cust_header = { 'User-Agent': generate_user_agent(device_type = "desktop", os=('mac', 'linux')) }
        website = requests.get(site, timeout=3, headers=cust_header)
        beautiful_website = BeautifulSoup(website.content, "html.parser")
        return(beautiful_website)

    except requests.exceptions.Timeout:
        print('Timeout')
        pass

    except requests.exceptions.TooManyRedirects:
        print('Too many redirections')
        pass

    except requests.exceptions.RequestException:
        print('Errrrrror')
        pass

def get_info(soup, site):

    '''get info about app'''

    try:
        title = soup.find(class_="product-header__title").text[1:-3].strip()
        dev = soup.find(class_="product-header__identity").text.strip()
        price = soup.find_all(class_="information-list__item")[-1].text.strip()
        rating = soup.find(class_="we-customer-ratings__averages__display").text.strip()
        no_of_ratings = soup.find(class_="we-customer-ratings__count").text.strip()
        info = soup.find(class_="section__description").text[15:].strip()
                # return tuple with infos
        return(title, dev, price, rating, no_of_ratings, info, site)

    except:
        # error handling (could be better)
        print("Errrrror")
        pass




def link_genre(site):

    '''generator function for genre url'''

    soup = site_open(site)
    genres = soup.find(id="genre-nav").find_all("a")
    for link in genres:
        yield link.get('href')


def link_app(site):

    '''generator function for app url'''

    soup = site_open(site)
    table = soup.find(id="selectedcontent").find_all("a")
    for link in table:
        yield (link.get('href'),)


start_page = "https://itunes.apple.com/de/genre/ios-b%C3%BCcher/id6018?mt=8"
categories = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
    'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z', '#']

def scrape_app_store(output, pause=float):

    '''create csv of app links
    output: file name of the output csv
    pause: a float determining the pause between the site requests'''

    f = open(output, 'a', newline = '')
    writer = csv.writer(f, dialect = 'excel', quoting=csv.QUOTE_NONNUMERIC)

    for i,link in enumerate(link_genre(start_page)):
        print('Genre: '+ str(i) + '.')

        for letter in categories:
            new_site = link + "&" + letter
            print('Now: ' + new_site + '.')

            print('Time for a pause: ' + str(pause) + ' seconds.')
            time.sleep(pause)

            for app in link_app(new_site):
                writer.writerow(app)

    f.close()
    print('Done!')
    return

scrape_app_store('apps.csv', pause=5)

# ####
def threading_splits(data, no_of_splits):

    '''return arrays of the data'''

    n = round(len(data)/no_of_splits)

    array_data = []
    for i in range(0, no_of_splits):
        j = data[(i-1)*n:i*n]
        array_data.append(j)

    return array_data

def threading_loop(data, writer):

    '''Called by a thread in app_info_crawl(). Loops through
    a sub-data array and writes output to a sub-csv file.'''

    for i,link in enumerate(data):
        try:
            info = get_info(site_open(link.strip('"')),link.strip('"'))
            writer.writerow(info)
        except:
            print("Errrrrror - could not write")
            continue
    print('Done here')
    return

def get_info_bulk(source, output, pause=float, num_threads=1):

    '''get bulk info for apps
    source: name of the input file
    output: name of the output file
    pause: float time to pause
    num_threads: number of threads'''

    f = open(source, 'r')
    data = f.readlines()
    random.shuffle(data)
    data = threading_splits(data, num_threads)

    for i,link_list in enumerate(data):

        #opens a csv file formatted as Links(i).csv according to the number of threads
        f = open('Links'+str(i)+'.csv', 'a', newline = '')
        writer = csv.writer(f, dialect='excel', quoting=csv.QUOTE_NONNUMERIC)

        #spawns thread and starts scrapping
        t = threading.Thread(target=threading_loop, args=(link_list,writer))
        t.start()

    print('Complete threading!')
    return

get_info_bulk(source='test.csv', output='info.csv', pause=5, num_threads=5)


f = open('Links1.csv', 'r')
d = f.readlines()
