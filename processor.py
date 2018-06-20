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
positions_small_set = set()
filtered = set()
info_emails = set()

res_folder = 'res/'
output_file = 'output/' + 'doc.csv'
failed_file = 'failed.txt'
names_file = res_folder + 'names_dict.txt'
last_names_file = res_folder + 'last_names_dict.txt'
positions_small_file = res_folder + 'positions.txt'
positions_file = res_folder + 'positions_extended.txt'
filter_file = res_folder + 'filter.txt'

phone_regex1 = ".*?(\(?\d{3}\D{0,3}\d{3}\D{0,3}\d{4}).*?"
phone_regex2 = '\D?(\d{0,3}?)\D{0,2}(\d{3})?\D{0,2}(\d{3})\D?(\d{4})$'
phone_regex3 = '(?:\+?(\d{1})?-?\(?(\d{3})\)?[\s-\.]?)?(\d{3})[\s-\.]?(\d{4})[\s-\.]?'
email_regex = "[a-z0-9\.\-+_]+@[a-z0-9\.\-+_]+\.[a-z]+"

stop_words = set(stopwords.words('english'))


def write_to_file():

    with open(output_file, 'a') as f:
        writer = csv.writer(f)

        while people:
            person = people.pop(0)
            info = person.get_info()
            writer.writerow(info)


def get_filter():
    with open(filter_file) as f:
        for line in f:
            filtered.add(line.strip('\n'))


def strip_string(str):
    return str.lstrip().rstrip()


def process_page(body, url):
    unfiltered_data = []

    # print('processing {}'.format(url))

    # body = soup.body

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


def is_data(entry):
    if is_name(entry) or is_position(entry) or is_phone_number(entry) or is_email(entry):
        return True

    return False


def filter_data(data):

    new_data = []
    new_data.append(data[1])

    for k in range(len(data)):
        if data[k] == new_data[len(new_data) - 1]:
            continue
        elif is_data(data[k]):
            new_data.append(data[k])

    return new_data


def remove_garbage(body):

    try:
        if body.footer:
            body.footer.decompose()

        if body.header:
            body.header.decompose()

        [comment.extract() for comment in body.findAll(text=lambda text: isinstance(text, Comment))]

        [x.decompose() for x in body.findAll('script')]

        [x.decompose() for x in body.findAll('style')]

        [x.decompose() for x in body.findAll('link')]

        [x.decompose() for x in body.findAll('img')]

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

                name = ''
                club_name = ''
                position = ''
                phone = ''
                email = ''
                info_email = ''
                misery_count += 1

                if entry == prev.name or entry == prev.email or (not is_name(entry) and not is_position(entry) and not is_phone_number(entry) and not is_email(entry)):
                    data = data[n:]
                    continue

                if is_club_name(data[n]):
                    club_name = data[n]

                if is_name(data[n]) and is_position(data[n]):

                    name, position = get_name_and_position(data, n)

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
                            if is_name(data[n - 1]) and is_position(data[n - 1]):
                                name, position = get_name_and_position(data, n - 1)
                            elif n > 0:
                                name = data[n - 1]
                                n += 1

                        elif is_name(data[n + 1]):
                            if is_name(data[n + 1]) and is_position(data[n + 1]):
                                name, position = get_name_and_position(data, n + 1)
                            else:
                                name = data[n + 1]
                                n += 2

                if is_info_email(data[n]):
                    info_email = data[n]

                if not is_phone_number(data[n]) and not is_email(data[n]):
                    n += 1

                if is_info_email(data[n]):
                    info_email = data[n]

                if not is_phone_number(data[n]) and not is_email(data[n]):
                    if n > 1:
                        n -= 2
                    else:
                        n += 1

                try:

                    if is_info_email(data[n]):
                        info_email = data[n]

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

                except Exception as e:
                    pass
                    # print(e, 'from inside')

                if not name and not position and not phone and not email:
                    continue

                elif email and (position or phone or name) and name != prev.name and 'club' not in name:
                    if n < 0:
                        n = 0

                    for person in people:
                        if name == person.name and email == person.email:
                            continue

                    name = parse_name(name)
                    email = parse_email(email)
                    phone = parse_phone(phone)
                    person = Person(name, position, phone, email, url)
                    people.append(person)
                    prev = person
                    # write_to_file()
                    data = data[n + 1:]
                    misery_count = 0
                    break

                if info_email and info_email not in info_emails:
                    if club_name is '' or club_name is None:
                        club_name = 'Club info'

                    info_emails.add(info_email)
                    phone = parse_phone(phone)
                    info_email = parse_email(info_email)
                    info_person = Person(club_name, position, phone, info_email, url)
                    people.append(info_person)
                    write_to_file()

        except Exception as e:
            # print(e)
            break

        write_to_file()


def get_name_and_position(data, n):
    delims = [':', ',', '-', '–']

    name = ''
    position = ''

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

    if is_position(data[n + 1]):
        position = position + ', ' + data[n + 1]
        n += 1

    return name, position


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
        if (word in names_set or word in last_names_set) and word not in stop_words:
            return True

    return False


def is_club_name(line):
    line = line.lower()
    words = ['club', 'country', 'road', 'river', 'bridge', 'hills', 'concierge', 'reception', 'desk', 'field', 'house']
    for word in words:
        if word in line:
            return True

    return False


def is_position(line):

    if is_email(line):
        return False

    line = line.lower()
    new_line = re.sub('[^a-zA-Z]', ' ', line)
    no_space = re.sub("[^a-zA-Z]+", '', new_line)

    if new_line.isspace():
        return False
    #
    # if no_space in positions_set:
    #     return True

    words = new_line.split(' ')

    if no_space in positions_set or set(words).intersection(positions_small_set):
        return True

    matches = 0

    for n in range(len(words) - 1):
        adj = words[n] + ' ' + words[n+1]
        if words[n] in positions_set or words[n + 1] in positions_set or adj in positions_set:
        # if adj in positions_set:
            matches += 1
            # return True
        if matches > 2:
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


def is_info_email(line):
    words = ['receptionesk', 'info', 'golfshop', 'proshop', 'shop', 'event', 'events', 'tournament']
    if is_email(line):
        for word in words:
            if word in line:
                return True

    return False


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

    with open(last_names_file) as f:
        for line in f:
            # names_set.add(line.strip('\n').lower())
            last_names_set.add(line.strip('\n').lower())


def get_positions():
    with open(positions_file) as f:
        for line in f:
            positions_set.add(line.strip('\n'))

    with open(positions_small_file) as f:
        for line in f:
            positions_small_set.add(line.strip('\n'))

    return positions_set


def get_phones_emails(body):
    unfiltered_phones = body.find_all(string=re.compile(phone_regex2))
    unfiltered_emails = body.find_all(string=re.compile(email_regex))

    phones = list(OrderedDict.fromkeys(unfiltered_phones))
    emails = list(OrderedDict.fromkeys(unfiltered_emails))

    return phones, emails