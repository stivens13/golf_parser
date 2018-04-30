from bs4 import BeautifulSoup, Comment
import re
from urllib.request import urlopen
from collections import OrderedDict
from nltk.corpus import stopwords
from Person import Person
import csv


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


xlsx_file = "database.xlsx"

phone_regex = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
email_regex = "[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"


def write_xlsx():

    if people:
        person = people.pop(0)
        info = person.get_info()
        with open("doc.csv", 'a') as f:
            writer = csv.writer(f)
            writer.writerow(info)


def get_urls():
    with open("test_urls.txt") as f:
        for line in f:
            urls.append(line)


def remove_garbage(body):

    try:
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
    except Exception as e:
        with open("failed.txt", "a") as f:
            f.write(body)
        print("Url failed: " + body)

    return body


def get_phones_emails(body):
    unfiltered_phones = body.find_all(string=re.compile(phone_regex))
    unfiltered_emails = body.find_all(string=re.compile(email_regex))

    phones = list(OrderedDict.fromkeys(unfiltered_phones))
    emails = list(OrderedDict.fromkeys(unfiltered_emails))

    return phones, emails


def strip_string(str):
    return str.lstrip().rstrip()


def create_people(data, url):

    prev = Person("dummy", "dummy", "dummy", "dummy", "dummy")

    for k in range(len(data) - 4):
        n = k

        data[n] = data[n].lstrip().rstrip()
        entry = data[n]

        name = ""
        position = ""
        phone = ""
        email = ""

        if is_name(data[n]) and is_position(data[n]) and (',' in data[n] or ':' in data[n]):
            words = []

            if ':' in data[n]:
                words = data[n].split(':')

            elif ',' in data[n]:
                words = data[n].split(',')

            if is_name(words[0]):
                name = words[0]
                position = words[1]
            else:
                position = words[0]
                name = words[1]

        elif is_name(data[n]) or is_position(data[n]):
            if is_name(data[n]):
                name = data[n]

                if is_position(data[n-1]):
                    position = data[n-1]
                    n += 1

                elif is_position(data[n+1]):
                    position = data[n+1]
                    n += 2

            elif is_position(data[n]):
                position = data[n]

                if is_name(data[n - 1]):
                    name = data[n - 1]
                    n += 1

                elif is_name(data[n + 1]):
                    name = data[n + 1]
                    n += 2

        if not is_phone_number(data[n]) and not is_email(data[n]):
            n += 1

        if not is_phone_number(data[n]) and not is_email(data[n]):
            n -= 2

        if is_phone_number(data[n]) or is_email(data[n]):
            if is_phone_number(data[n]):
                phone = data[n]

                if is_email(data[n - 1]):
                    email = data[n - 1]

                elif is_email(data[n + 1]):
                    email = data[n + 1]

            elif is_email(data[n]):
                email = data[n]

                if is_phone_number(data[n - 1]):
                    phone = data[n - 1]

                elif is_phone_number(data[n + 1]):
                    phone = data[n + 1]

        if not name and not position and not phone and not email:
            continue

        elif name and (position or phone or email) and name != prev.name:
            person = Person(name, position, phone, email, url)
            people.append(person)
            prev = person
            write_xlsx()


def in_filter(line):

    line = line.lower().strip()
    line = re.sub("[^a-zA-Z]+", "", line)
    if line in filtered:
        return True

    return False


def is_name(line):
    line = line.lower().strip(':').strip('/')
    words = line.split(' ')

    for word in words:
        if word in name_list and word not in stop_words:
            return True

    return False


def is_position(line):
    # line = line.lower().replace("/", "")
    line = line.lower().replace("/", "").replace(':', '').replace(',', '')
    # print(line)

    no_space = re.sub("[^a-zA-Z]+", "", line)
    # return [position in line for position in positions_list]
    if no_space in positions_list:
        return True

    words = line.split(' ')
    # print(positions_list)
    for word in words:
        if word in positions_list:
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


def get_positions():
    with open("positions.txt") as f:
        for line in f:
            positions_list.add(line.strip('\n'))


def get_filter():
    with open("filter.txt") as f:
        for line in f:
            filtered.add(line.strip('\n'))


def get_soup(url):

    html = urlopen(url)
    soup = BeautifulSoup(html, "html.parser")
    return soup


def start_scaping():

    for url in urls:

        unfiltered_data = []

        soup = ""

        try:
            soup = get_soup(url)
            if soup is None:
                continue
        except Exception as e:
            with open("failed.txt", "a") as f:
                f.write(url)
            print("Url failed: " + url)
            continue

        body = soup.body

        print("url " + url + " is being processed")

        try:
            body = remove_garbage(body)

        except Exception as e:
            with open("failed.txt", "a") as f:
                f.write(url)
            print("Url failed: " + url)
            continue

        body.prettify()

        # print(body)

        # [elem.string.replace_with(str(elem['href']).replace('mailto:', '')) if str(elem['href']).replace('mailto:',
        #                                                                                                  '') != str(
        #     elem.string) and elem.string else '' for elem in body.select('a[href^="mailto"]')]

        # [elem.string.replace_with(str(elem['href']).replace('mailto:', '')) if elem.string else '' for elem in body.select('a[href^="mailto"]')]

        for elem in body:
            if elem.string:
                elem.string.replace_with( str(elem.string).lstrip().rstrip() )

        for elem in body.select('a[href^="mailto"]'):
            # print(elem)
            if elem.string:
                elem.string.replace_with(str(elem['href']).replace('mailto:', ''))
                # print(elem.string)
            else:
                for l in elem:
                    if l.string and 'Email' in str(l.string):
                        # print(l.string)
                        l.replace_with(str(elem['href']).replace('mailto:', ''))




        for child in body.descendants:
            if child.string is None or str(child.string).isspace() or len(str(child.string).strip()) > 50 or len(
                    str(child.string).strip()) < 3 or in_filter(str(child.string)):
                continue

            unfiltered_data.append(  re.sub('\s+', ' ', str(child.string).lstrip().rstrip()) )
            # unfiltered_data.append(str(child.string).lstrip().rstrip() )

        data = list(OrderedDict.fromkeys(unfiltered_data))
        # for d in data:
        #     print(d)
        create_people(data, url)


def main():

    get_names()
    get_positions()
    get_filter()

    get_urls()

    start_scaping()


main()
