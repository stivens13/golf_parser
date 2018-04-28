# import scrapy
# import pandas as pd
# import requests

from bs4 import BeautifulSoup, Comment
import re
from urllib.request import urlopen
from collections import OrderedDict
from nltk.corpus import stopwords
from Person import Person

urls = []
people = []
name_list = set()
positions_list = set()
filtered = set()
stop_words = set(stopwords.words('english'))
stop_words.add('ext')
stop_words.add('real estate')
stop_words.add('bar')
stop_words.add('of')


phone_regex = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
email_regex = "[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"


def get_urls():
    with open("test_urls.txt") as f:
        for line in f:
            urls.append(line)


def remove_garbage(body):
    # body = soup.body
    # soup.head.decompose()
    if body.footer:
        body.footer.decompose()

    if body.header:
        body.header.decompose()

    comments = body.findAll(text=lambda text: isinstance(text, Comment))
    [comment.extract() for comment in comments]

    while body.script:
        body.script.decompose()
    while body.style:
        body.style.decompose()
    while body.link:
        body.link.decompose()
    while body.img:
        body.img.decompose()

    return body

# def get_person(data):
#     for line in data:
#         if()


def get_phones_emails(body):
    unfiltered_phones = body.find_all(string=re.compile(phone_regex))
    unfiltered_emails = body.find_all(string=re.compile(email_regex))

    phones = list(OrderedDict.fromkeys(unfiltered_phones))
    emails = list(OrderedDict.fromkeys(unfiltered_emails))

    return phones, emails


def create_people(data):

    new_data = []

    for entry in data:

        # print(entry)
        # words = entry.split(' ')

        # for word in words:

        if is_name(entry):
            print(entry)

        # if is_position(entry) == 1 or is_phone_number(entry) or is_email(entry):
        #     new_data.append(entry)
        #     break

    # for entry in new_data:
    #     print(entry)


def in_filter(line):
    # print(line)
    line = line.lower()
    words = str(line).split(' ')
    for word in words:
        if word in filtered:
            return True

    return False


def is_name(line):
    # if ',' or ':' in line:
    #     return 2

    line = line.lower()
    words = line.split(' ')

    for word in words:
        if word in name_list and word not in stop_words:
            return True

    return False


def is_position(line):
    line = line.lower()
    # return [position in line for position in positions_list]

    # print(positions_list)
    for position in positions_list:
        if position in line:
            return True

    return False


def is_phone_number(line):
    return bool(re.search(phone_regex, line))


def is_email(line):
    return bool(re.search(email_regex, line))


def get_names():
    with open("names_dict.txt") as f:
        for line in f:
            name_list.add(line.strip('\n').lower())

    # with open("last_names_dict.txt") as ff:
    #     for line in ff:
    #         name_list.append(line.strip('\n'))

    # print((name_list))


def get_positions():
    with open("positions.txt") as f:
        for line in f:
            positions_list.add(line.strip('\n'))


def get_filter():
    with open("filter.txt") as f:
        for line in f:
            filtered.add(line.strip('\n'))


def get_soup(url):

    try:
        html = urlopen(url)
        type(html)
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except Exception as e:
        with open("failed.txt", "a") as f:
            f.write(url + " " + e.__traceback__ + "\n")
        print("Url failed: " + url)

    # soup = BeautifulSoup(requests.get(url).text, "html.parser")


def start_scaping():
    unfiltered_data = []

    for url in urls:

        soup = get_soup(url)
        if soup is None:
            continue

        body = soup.body

        print("url " + url + " is being processed")

        body = remove_garbage(body)

        body.prettify()

        [elem.string.replace_with(str(elem['href']).replace('mailto:', '')) if str(elem['href']).replace('mailto:',
                                                                                                         '') != str(
            elem.string) else '' for elem in body.select('a[href^="mailto"]')]

        for child in body.descendants:
            if child.string is None or str(child.string).isspace() or len(str(child.string)) > 50 or len(
                    str(child.string).strip()) < 3 or in_filter(str(child.string)):
                continue

            unfiltered_data.append(child.string)

        data = list(OrderedDict.fromkeys(unfiltered_data))
        # for d in data:
        #     print(d)
        create_people(data)


def main():

    get_names()
    get_positions()
    get_filter()

    get_urls()

    start_scaping()


main()