# -*- coding: utf-8 -*-
from grabber import Grabber
import gevent.monkey;
import processor
from bs4 import BeautifulSoup, SoupStrainer
from urllib.request import urlopen
import time
import progressbar
import multiprocessing
import csv
import datetime

grab = Grabber()

# bar1 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
# bar2 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
# bar3 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)

logging = True
processor.logging = logging
grab.logging = logging


# output_file = 'output/' + 'doc.csv'
output_file = 'output/doc {}.csv'.format(str(datetime.datetime.now())[:-7])
failed_file = 'failed.txt'
res = 'res/'


class Scraper:

    souper_not_done = True

    souped = 0
    processed = 0

    pages = []
    urls = []
    bodies = []

    url_file = res + 'all_urls.txt'
    # url_file = res + 'urls.txt'
    url_test_file = res + 'test_urls.txt'

    # pages_mult = multiprocessing.Queue()
    # bodies_mult = multiprocessing.Queue()
    # pages_mult = multiprocessing.Queue()

    def __init__(self):
        self.souped = 0
        self.processed = 0
        self.main()

    def create_output_file(self):
        # print(str(datetime.datetime.now()))

        # cur_time = str(datetime.datetime.now())[:-7]
        # output_file = 'output/' + 'doc ' + cur_time + '.csv'

        processor.output_file = output_file
        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Position', 'Phone', 'Email', 'Website'])

    def get_urls(self):
        with open(self.url_file) as f:
            for line in f:
                self.urls.append(line)

        return self.urls

    @staticmethod
    def get_soup(url):

        html = urlopen(url)
        soup = BeautifulSoup(html, 'lxml')
        return soup

    def soupify(self, page):
        try:
            url = page.geturl()
            strain = SoupStrainer('body')

            # self.bodies_mult.put([BeautifulSoup(page, 'html.parser').body, url])
            self.bodies.append([BeautifulSoup(page, 'lxml', parse_only=strain), url])

            # self.bodies.append([BeautifulSoup(page, 'html.parser'), url])

        except Exception as e:
            print(e)

    def grabbing(self):

        print('Grabbing started')

        url_chunks = [self.urls[x:x + 200] for x in range(0, len(self.urls), 200)]

        for _urls in url_chunks:
            grabber_jobs = grab.worker(_urls)
            gevent.joinall(grabber_jobs, timeout=20)
            grab.print_urls_grabbed()

    def souping(self):

        print('Scraping is started')
        i = 0
        souping_jobs = []

        # while grab.grabber_not_done or self.pages_mult:
        while grab.grabber_not_done or grab.more_pages():

            # i += 1

            # if self.pages_mult.qsize() > 0:
            if grab.more_pages():

                try:
                    # souping_jobs.append(gevent.spawn(self.soupify, self.pages_mult.get()))
                    page = grab.get_page()
                    souping_jobs.append(gevent.spawn(self.soupify, page))
                    self.souped += 1
                    if logging:
                        print('{} souped {}'.format(self.souped, page.geturl()))
                    # print('processed {}'.format(page.geturl()))

                # paging.append(gevent.spawn(soupify, page))
                except Exception as e:
                    print(e)
            else:
                print('souper sleeps for 1 secs')
                gevent.sleep(1)

        print('SOUPING IS DONE')

        return souping_jobs

    def processing(self):
        print('Processing started')
        processing_jobs = []

        # while self.souper_not_done or self.bodies_mult:
        while self.souper_not_done or self.bodies:

            # if self.bodies_mult.qsize() > 0:
            if self.bodies:
                # body = self.bodies_mult.get()
                body = self.bodies.pop(0)

                try:
                    processing_jobs.append(gevent.spawn(processor.process_page, body[0], body[1], self.processed))
                    self.processed += 1
                except Exception as e:
                    print(e)
            else:
                print('processor sleeps for 1 secs')
                gevent.sleep(1)

        return processing_jobs

    def init_grabbing(self):
        t = time.time()

        grabber_jobs = grab.worker(self.urls)
        gevent.joinall(grabber_jobs)


        grab.grabber_not_done = False

        # grab.worker_faster(self.urls)

        num = grab.pages_grabbed
        final = round(time.time() - t)
        if num:
            print('{} urls grabbed in {} sec, {:3f} sec per page'.format(num,
                                                                         final,
                                                                         final / num))

    def init_souping(self):
        t = time.time()
        souping_jobs = self.souping()
        gevent.joinall(souping_jobs)
        # gevent.joinall(souping_jobs, timeout=40)
        self.souper_not_done = False
        final = round(time.time() - t)
        if self.souped:
            print('{} pages souped in {} sec, {:3f} sec per page'.format(self.souped,
                                                                         final,
                                                                         final / self.souped))

    def init_processing(self):
        t = time.time()
        processing_jobs = self.processing()
        gevent.joinall(processing_jobs)
        # gevent.joinall(processing_jobs, timeout=40)
        final = round(time.time() - t)
        if self.processed is not 0:
            print('{} pages processed in {} sec, {:3f} sec per page'.format(self.processed, final,
                                                                            final / self.processed))

    def async_starter(self):

        self.get_urls()

        procs = [gevent.spawn(self.init_grabbing),
                 gevent.spawn_later(3, self.init_souping),
                 gevent.spawn_later(3, self.init_processing)]

        gevent.joinall(procs)

    def sync_starter(self):

        self.url_file = self.url_test_file
        self.get_urls()

        for url in self.urls:

            try:
                body = self.get_soup(url)
                if body is None:
                    continue
            except Exception as e:
                with open(failed_file, "a") as f:
                    f.write(url)
                print("Url failed: " + url)
                continue

            # body = soup.body

            print("url " + url + " is being processed")

            processor.process_page(body, url)

    def main(self):
        t = time.time()

        self.create_output_file()

        processor.get_names()
        processor.get_positions()
        processor.get_filter()

        # self.sync_starter()
        self.async_starter()

        final = round(time.time() - t)

        print('Parser took that many seconds to complete: ', final/60)


if __name__ == "__main__":
    m = Scraper()
