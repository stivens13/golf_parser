import gevent.monkey; gevent.monkey.patch_all()
from urllib.request import urlopen

failed = []


class Grabber:

    pages = []

    pages_grabbed = 0

    grabber_not_done = True

    def __init__(self):
        self.pages_grabbed = 0

    def get_pages(self):
        return self.pages

    def get_page(self):
        return self.pages.pop(0)

    def print_head(self, url):

        try:

            data = urlopen(url)

            if data.getcode() == 200:
                # self.pages.put(data) # for multiprocessing
                self.pages.append(data)

            self.pages_grabbed += 1

        except Exception as e:
            # print(e, " ", url)
            failed.append(url)

    def print_urls_grabbed(self):
        print('Grabber grabbed {} pages'.format(self.pages_grabbed))

    def worker(self, urls): #, pages):
        print('Grabber is started')

        # self.pages = pages # for multiprocessing

        grabber_jobs = [gevent.spawn(self.print_head, _url) for _url in urls]
        return grabber_jobs

    def more_pages(self):
        return len(self.pages) > 0
