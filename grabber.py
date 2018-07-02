import gevent.monkey; gevent.monkey.patch_all()
from urllib.request import urlopen


class Grabber:

    pages = []
    failed = []

    pages_grabbed = 0
    grabbing = 0

    grabber_not_done = True
    logging = True

    def __init__(self):
        self.pages_grabbed = 0

    def get_pages(self):
        return self.pages

    def get_page(self):
        return self.pages.pop(0)

    def print_head(self, url):

        try:

            while self.grabbing > 200:
                # print('sleeping')
                gevent.sleep(1)

            self.grabbing += 1


            data = urlopen(url)

            if data.getcode() == 200:
                # self.pages.put(data) # for multiprocessing
                self.pages.append(data)
                self.pages_grabbed += 1

                if self.logging:
                    print('{} grabbed {}'.format(self.pages_grabbed, url))

            else:
                self.failed.append(url)

            self.grabbing -= 1

        except Exception as e:
            # print(e, " ", url)
            self.failed.append(url)
            self.grabbing -= 1

    def print_urls_grabbed(self):
        print('Grabber grabbed {} pages and {} failed'.format(self.pages_grabbed, len(self.failed)))
        self.failed = []

    def worker(self, urls): #, pages):
        print('Grabber is started')

        # self.pages = pages # for multiprocessing

        grabber_jobs = [gevent.spawn(self.print_head, _url) for _url in urls]
        return grabber_jobs

    def more_pages(self):
        return len(self.pages) > 0
