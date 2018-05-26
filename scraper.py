# -*- coding: utf-8 -*-
from grabber import Grabber
import gevent.monkey;
import processor
from bs4 import BeautifulSoup
from urllib.request import urlopen
import time
import progressbar

import csv

grab = Grabber()

bar1 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
bar2 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)
bar3 = progressbar.ProgressBar(max_value=progressbar.UnknownLength)


output_file = "doc.csv"
url_file = 'urls.txt'
# url_file = "test_urls.txt"
failed_file = "failed.txt"


class Scraper:

    souper_not_done = True

    souped = 0
    processed = 0

    pages = []
    urls = []
    bodies = []

    def __init__(self):
        self.souped = 0
        self.processed = 0
        self.main()

    def create_output_file(self):
        with open(output_file, 'w') as f:
            writer = csv.writer(f)
            writer.writerow(['Name', 'Position', 'Phone', 'Email', 'Website'])

    def get_urls(self):
        with open(url_file) as f:
            for line in f:
                self.urls.append(line)

        return self.urls


    def get_soup(self, url):

        html = urlopen(url)
        soup = BeautifulSoup(html, "html.parser")
        return soup


    def sync_start_scraping(self):

        for url in self.urls:

            try:
                soup = self.get_soup(url)
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

    def soupify(self, page):
        try:
            url = page.geturl()
            # print('soupifying {}'.format(url))
            # bar1.update(i, url)
            self.bodies.append([BeautifulSoup(page, 'html.parser').body, url])
        except Exception as e:
            print(e)



    def souping(self):

        print('Scraping is started')
        i = 0
        souping_jobs = []
        while grab.grabber_not_done or grab.more_pages():
        # for page in grab.get_pages():
            i += 1
            # bar2.update(i)
            if grab.more_pages():
                try:
                    souping_jobs.append(gevent.spawn(self.soupify, grab.get_page()))
                    self.souped += 1
                # paging.append(gevent.spawn(soupify, page))
                except Exception as e:
                    print(e)
            else:
                print('souper sleeps for 3 secs')
                gevent.sleep(3)


        self.souper_not_done = False
        return souping_jobs

    def breading(self):
        print('Processing started')
        processing_jobs = []

        while self.souper_not_done or self.bodies:

            if self.bodies:
                body = self.bodies.pop(0)

                try:
                    processing_jobs.append(gevent.spawn(processor.process_page, body[0], body[1]))
                    self.processed += 1
                except Exception as e:
                    print(e)
            else:
                print('processor sleeps for 3 secs')
                gevent.sleep(3)

        return processing_jobs
            # [gevent.spawn(processor.process_page, body[0], body[1]) for body in bodies]

    def init_grabbing(self):
        t = time.time()
        grabber_jobs = grab.worker(self.urls)
        gevent.joinall(grabber_jobs, timeout=20)
        grab.print_urls_grabbed()
        grab.grabber_not_done = False
        num = grab.pages_grabbed
        final = round(time.time() - t)
        print('{} urls grabbed in {} sec, {} sec per page'.format(num, final, final / num ))

    def init_souping(self):
        t = time.time()
        souping_jobs = self.souping()
        gevent.joinall(souping_jobs, timeout=20)
        final = round(time.time() - t)
        print('{} pages souped in {} sec, {} sec per page'.format(self.souped, final, final /  self.souped))

    def init_processing(self):
        t = time.time()
        processing_jobs = self.breading()
        gevent.joinall(processing_jobs, timeout=20)
        final = round(time.time() - t)
        print('{} pages souped in {} sec, {} sec per page'.format(self.processed, final, final / self.processed))


    def green_start_scraping(self):

        procs = [gevent.spawn(self.init_grabbing), gevent.spawn_later(10, self.init_souping), gevent.spawn_later(10, self.init_processing)]

        gevent.joinall(procs)

        # grabber_jobs = grab.worker()
        # gevent.joinall(grabber_jobs, timeout=20)
        #
        # souping_jobs = self.souping()
        # gevent.joinall(souping_jobs, timeout=20)
        #
        # processing_jobs = self.breading()
        # gevent.joinall(processing_jobs, timeout=20)

        # print('Pages souped', self.souped)
        # print('Pages souped', self.souped)

    def sync_starter(self):
        self.sync_start_scraping()

    def async_starter(self):
        # grab.start_grabbing()
        # job = gevent.spawn_later(5, green_start_scraping())
        #
        # gevent.joinall(job, timeout=5)
        self.green_start_scraping()

    def main(self):
        t = time.time()

        self.create_output_file()

        processor.get_names()
        processor.get_positions()
        processor.get_filter()
        self.get_urls()

        self.async_starter()

        final = round( time.time() - t )

        print('time elapsed: ', final)


if __name__ == "__main__":
    m = Scraper()
