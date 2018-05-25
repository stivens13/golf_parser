# -*- coding: utf-8 -*-
import grabber
import gevent.monkey;
import processor
from bs4 import BeautifulSoup
from urllib.request import urlopen

import csv


pages = []
urls = []


output_file = "doc.csv"
# url_file = 'urls.txt'
url_file = "test_urls.txt"
failed_file = "failed.txt"


xlsx_file = "database.xlsx"


def create_output_file():
    with open(output_file, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Position', 'Phone', 'Email', 'Website'])


def get_urls():
    with open(url_file) as f:
        for line in f:
            urls.append(line)

    return urls


def get_soup(url):

    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def sync_start_scraping():

    for url in urls:

        try:
            soup = get_soup(url)
            if soup is None:
                continue
        except Exception as e:
            with open(failed_file, "a") as f:
                f.write(url)
            print("Url failed: " + url)
            continue

        body = soup.body

        print("url " + url + " is being processed")

        processor.process_page(body, url)


def green_start_scraping():
    while grabber.grabber_not_done or grabber.pages:

        while grabber.pages:
            try:

                page = grabber.pages.pop(0)
                soup = BeautifulSoup(page.read(), 'html.parser')
                print('processing {}'.format(page.geturl()))
                processor.process_page(soup.body, page.geturl())
            except Exception as e:
                print('Hi there')
                print(e)

        gevent.sleep(5)

def sync_starter():
    sync_start_scraping()


def async_starter():
    grabber.start_grabbing()
    job = gevent.spawn_later(5, green_start_scraping())

    gevent.joinall(job, timeout=5)



def main():

    create_output_file()

    processor.get_names()
    processor.get_positions()
    processor.get_filter()
    get_urls()

    sync_starter()


if __name__ == "__main__":
    main()
