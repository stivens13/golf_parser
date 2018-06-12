from bs4 import BeautifulSoup, Comment
from Person import Person
# import scraper
import re
from collections import OrderedDict
from nltk.corpus import stopwords
import csv

# people = scraper.people
people = []

names_set = set()
last_names_set = set()
positions_set = set()
filtered = set()

output_file = 'doc.csv'
failed_file = 'failed.txt'
names_file = 'names_dict.txt'
last_names_file = 'last_names_dict.txt'
# positions_file = "positions.txt"
positions_file = 'positions_extended.txt'
filter_file = 'filter.txt'

phone_regex1 = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
phone_regex2 = '\D?(\d{0,3}?)\D{0,2}(\d{3})?\D{0,2}(\d{3})\D?(\d{4})$'
phone_regex3 = '(?:\+?(\d{1})?-?\(?(\d{3})\)?[\s-\.]?)?(\d{3})[\s-\.]?(\d{4})[\s-\.]?'
email_regex = "[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"

stop_words = set(stopwords.words('english'))
# stop_words.add('ext')
# stop_words.add('real estate')
# stop_words.add('bar')
# stop_words.add('of')


def write_to_file():

    if people:
        person = people.pop(0)
        info = person.get_info()
        f = open(output_file, 'a')
        writer = csv.writer(f)
        writer.writerow(info)
        f.close()
        # with open(output_file, 'a') as f:
        #     writer = csv.writer(f)
        #     writer.writerow(info)


def get_filter():
    with open(filter_file) as f:
        for line in f:
            filtered.add(line.strip('\n'))


def strip_string(str):
    return str.lstrip().rstrip()


def process_page(soup, url):
    unfiltered_data = []

    # print('processing {}'.format(url))

    body = soup.body

    try:
        body = remove_garbage(body)

    except Exception as e:
        with open(failed_file, "a") as f:
            f.write(url)
        print("Url failed: " + url)
        return

    body.prettify()

    for elem in body:
        if elem.string:
            elem.string.replace_with(str(elem.string).lstrip().rstrip())

    for elem in body.select('a[href^="mailto"]'):
        # print(elem.string)
        if elem.string and ('Email' in str(elem.string) or not is_email(elem.string)):
            # print(elem.string)
            elem.string.replace_with(str(elem['href']).replace('mailto:', ''))
        else:
            for l in elem:
                if l.string and ('Email' in str(l.string) or not is_email(l.string)):
                    # print(l.string)
                    l.replace_with(str(elem['href']).replace('mailto:', ''))

    for child in body.descendants:
        if child.string is None or str(child.string).isspace() or len(str(child.string).strip()) > 60 or len(
                str(child.string).strip()) < 3 or in_filter(str(child.string)) or str(child.string) == unfiltered_data[-1:]:
            continue

        unfiltered_data.append(re.sub('\s+', ' ', str(child.string).lstrip().rstrip()))

    if len(unfiltered_data) > 10:
        data = filter_data(unfiltered_data)
        # data = list(OrderedDict.fromkeys(unfiltered_data))

        create_people(data, url.strip('"'))
        # create_people(data, url.strip('"'))


def filter_data(data):

    new_data = []
    new_data.append(data[1])

    for k in range(len(data)):
        if data[k] == new_data[len(new_data) - 1]:
            continue
        else:
            new_data.append(data[k])

    return new_data


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
        with open(failed_file, "a") as f:
            f.write(body)
        print("Url failed: " + body)

    return body


def create_people(data, url):

    # print('processing {}'.format(url))

    prev = Person("dummy", "dummy", "dummy", "dummy", "dummy")

    misery_count = 0

    while(data):

        if misery_count > 300:
            break

        try:
            for k in range(len(data)):
                n = k

                data[n] = data[n].lstrip().rstrip()
                entry = data[n]

                name = ""
                position = ""
                phone = ""
                email = ""
                misery_count += 1

                if entry == prev.name or entry == prev.email or (not is_name(entry) and not is_position(entry) and not is_phone_number(entry) and not is_email(entry)):
                    data = data[n:]
                    continue

                if is_name(data[n]) and is_position(data[n]): # and (',' in data[n] or ':' in data[n]):
                    words = []

                    delims = [':', ',', '-', '–']

                    for delim in delims:
                        if delim in data[n]:
                            words = data[n].split(delim)

                            if is_name(words[0]):
                                name = words[0]
                                position = words[1]
                                break
                            else:
                                position = words[0]
                                name = words[1]
                                break

                    if name == '' or None:
                        # print('else')
                        words = data[n].split()
                        if is_name(words[0]):
                            name = words[0] + ' ' + words[1]
                            if is_position(' '.join(words[2:])):
                                position = ' '.join(words[2:])

                    # if ':' in data[n]:
                    #     words = data[n].split(':')
                    #
                    # elif ',' in data[n]:
                    #     words = data[n].split(',')
                    #
                    # elif '-' in data[n]:
                    #     words = data[n].split('-')
                    #
                    # elif '–' in data[n]:
                    #     words = data[n].split('–')



                    if is_position(data[n + 1]):
                        position = position + ', ' + data[n + 1]
                        n += 1

                elif (is_name(data[n]) or is_position(data[n])) and not is_email(data[n]):
                    if is_name(data[n]):
                        name = data[n]

                        if is_position(data[n - 1]) and n > 0:
                            position = data[n - 1]
                            n += 1

                        elif is_position(data[n+1]):
                            position = data[n+1]
                            n += 2

                    elif is_position(data[n]):
                        position = data[n]

                        if is_name(data[n - 1]) and n > 0:
                            name = data[n - 1]
                            n += 1

                        elif is_name(data[n + 1]):
                            name = data[n + 1]
                            n += 2

                if not is_phone_number(data[n]) and not is_email(data[n]):
                    n += 1

                if not is_phone_number(data[n]) and not is_email(data[n]):
                    if n > 1:
                        n -= 2
                    else:
                        n += 1

                if is_phone_number(data[n]) and is_email(data[n]):
                    words = data[n].split(' ')
                    for word in words:
                        if is_phone_number(word):
                            phone = word

                        elif is_email(word):
                            email = word

                elif is_phone_number(data[n]) or is_email(data[n]):
                    if is_phone_number(data[n]):
                        phone = data[n]

                        if is_email(data[n - 1]) and n > 0:
                            email = data[n - 1]
                            n -= 1

                        elif is_email(data[n + 1]):
                            email = data[n + 1]
                            n += 1

                    elif is_email(data[n]):
                        email = data[n]

                        if is_phone_number(data[n - 1]) and n > 0:
                            phone = data[n - 1]
                            n -= 1

                        elif is_phone_number(data[n + 1]):
                            phone = data[n + 1]
                            n += 1

                if not name and not position and not phone and not email:
                    continue

                elif name and (position or phone or email) and name != prev.name:
                    if n < 0:
                        n = 0

                    name = parse_name(name)
                    email = parse_email(email)
                    phone = parse_phone(phone)
                    person = Person(name, position, phone, email, url)
                    people.append(person)
                    prev = person
                    write_to_file()
                    data = data[n + 1:]
                    misery_count = 0
                    break

        except Exception as e:
            break


def in_filter(line):

    line = line.lower().strip()
    line = re.sub("[^a-zA-Z]+", "", line)
    if line in filtered:
        return True

    return False


def is_name(line):
    line = line.lower().strip(':').strip('/')
    words = line.split(' ')

    # if words[1] in last_names_set:
    #     return True

    for word in words:
        if word in names_set and word not in stop_words:
            return True

    return False


def is_position(line):
    # line = line.lower().replace("/", "")
    # line = line.lower().replace("/", " ").replace(':', ' ').replace(',', ' ')
    # line = re.sub('\s+', ' ', line)
    # print(line)

    if is_email(line):
        return False

    line = line.lower()
    new_line = re.sub('[^a-zA-Z]', ' ', line)

    no_space = re.sub("[^a-zA-Z]+", '', new_line)
    # return [position in new_line for position in positions_list]
    if no_space in positions_set:# or line.strip() in positions_list:
        return True

    words = new_line.split(' ')

    # print(positions_list)
    for n in range(len(words) - 1):
        adj = words[n] + ' ' + words[n+1]
        if words[n] in positions_set or words[n + 1] in positions_set or adj in positions_set:
            return True

    return False


def is_phone_number(line):
    is_phone = bool(re.search(phone_regex1, line)) or bool(re.search(phone_regex2, line))
    # is_phone = bool(re.search(phone_regex2, line))
    if is_phone:
        return True
    else:
        words = line.split(' ')
        for word in words:
            if bool(re.search(phone_regex1, word)) or bool(re.search(phone_regex2, word)):
                return True

    return False


def is_email(line):
    return bool(re.search(email_regex, line))


def parse_name(line):
    return re.sub("[^ a-zA-Z]+", "", strip_string(line))

def parse_email(line):
    words = line.split(' ')
    for word in words:
        if is_email(word):
            return word

def parse_phone(str):
    filts = ['|', 'Phone', 'Cell:', '.']
    for filt in filts:
        str = str.strip(filt)
    return str

    # return str.strip('|').strip('Phone')


def get_names():
    with open(names_file) as f:
        for line in f:
            names_set.add(line.strip('\n').lower())

    # return name_list

    # with open("last_names_dict.txt") as f:
    #     for line in f:
    #         names_set.add(line.strip('\n').lower())
    #         # last_names_set.add(line.strip('\n').lower())


def get_positions():
    with open(positions_file) as f:
        for line in f:
            positions_set.add(line.strip('\n'))

    return positions_set


def get_phones_emails(body):
    unfiltered_phones = body.find_all(string=re.compile(phone_regex2))
    unfiltered_emails = body.find_all(string=re.compile(email_regex))

    phones = list(OrderedDict.fromkeys(unfiltered_phones))
    emails = list(OrderedDict.fromkeys(unfiltered_emails))

    return phones, emails