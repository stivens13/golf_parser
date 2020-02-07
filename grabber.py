import gevent.monkey; gevent.monkey.patch_all()
from urllib.request import urlopen
import pandas as pd
import concurrent.futures
import requests
import time


class Grabber:

    pages = []
    failed = []

    pages_grabbed = 0
    grabbing = 0

    out = []
    CONNECTIONS = 100
    TIMEOUT = 5

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

    def load_url(self, url, timeout):
        res = requests.get(url, timeout=timeout)
        return res

    def get_data(self, _urls):

        with concurrent.futures.ThreadPoolExecutor(max_workers=self.CONNECTIONS) as executor:
            future_to_url = (executor.submit(self.load_url, url, self.TIMEOUT) for url in _urls)
            num_of_urls = 0
            for future in concurrent.futures.as_completed(future_to_url):
                try:
                    num_of_urls += 1

                    print('Nothing happens in get_data()')
                    fut = future.result()
                    data = fut.status_code
                    if data == 200:
                        # self.pages.put(data) # for multiprocessing
                        self.pages.append(fut.content)
                        self.pages_grabbed += 1

                        if self.logging:
                            print('{} grabbed {}'.format(self.pages_grabbed, fut.url))

                    if int(data) > 400:
                        self.failed.append(fut.url)

                    print(num_of_urls, data)

                except Exception as exc:
                    data = str(type(exc))
                    self.failed.append(fut.url)

                finally:
                    self.out.append(data)
                    print(str(len(self.out)), end="\r")

    def worker_faster(self, urls):

        print('Started initial grabbing')
        time1 = time.time()
        self.get_data(urls)
        time2 = time.time()

        print(f'Took {time2-time1:.2f} s')

        if self.failed:
            self.get_data(self.failed)

        self.grabber_not_done = False

        print(pd.Series(self.out).value_counts())

    def more_pages(self):
        return len(self.pages) > 0
