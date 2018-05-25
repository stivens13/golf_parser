import gevent.monkey; gevent.monkey.patch_all()
from urllib.request import urlopen
from bs4 import BeautifulSoup

failed = []
pages = []
urls = []

grabber_not_done = True

url_file = "urls.txt"

def get_urls():
    with open(url_file) as f:
        for line in f:
            urls.append(line)

    # return urls


def print_head(url):
    print('Starting {}'.format(url))
    try:
        data = urlopen(url)
        # print(data.geturl())
        pages.append(data)
        # soup = BeautifulSoup(data, 'html.parser')
        # print('{}: {} bytes: {}'.format(url, len(data.read()), soup.title))
        # print(url)
    except Exception as e:
        print(e, " ", url)
        failed.append(url)


def worker(_urls):
    jobs = [gevent.spawn(print_head, _url) for _url in _urls]

    gevent.joinall(jobs, timeout=20)

def start_grabbing():
    get_urls()
    worker(urls)
    print('Grabber is done')
    grabber_not_done = False
    return pages