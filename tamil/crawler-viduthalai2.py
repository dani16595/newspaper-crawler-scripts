# -*- coding: utf-8 -*-
import urllib
import os
import re
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
import requests
import sys
import time
from pprint import pprint, pformat
FORMAT_STRING = "%(levelname)-8s:%(name)-8s.%(funcName)-8s>> %(message)s"

import logging
logging.basicConfig(format=FORMAT_STRING)
log = logging.getLogger(__name__)
log.setLevel(logging.CRITICAL)

from crawler import Crawler, mkdir

uid_ = 0
name = '{}'.format(uid_)
    
class ViduthalaiCrawler(Crawler):

    def __init__(self, root_url):
        root_dir = os.path.basename(__file__).replace('crawler-', '').replace('.py', '')
        super().__init__(root_url = root_url,
                         root_dir= root_dir)
        
    def extract_year_month(self, page_link, soup):
        global uid_
        year, month = '0000', '00'
        timestamp = soup.find(class_='date')

        timestamp = timestamp.find(class_='created')
        log.info(timestamp.text)
        m = re.search('.*, \d+ (.*) (\d{4})', timestamp.text.strip())
        if m:
            log.debug(pformat(m))
            month, year = m.groups()

        for d in self.SUBDIRS:
            mkdir('{}/{}/{}'.format(d, year, month))

        return year, month

    def process_page(self, page_name, soup):
        global uid_
        # remove all javascript and stylesheet code
        for script in soup(["script", "style"]): 
            script.extract()

        content = soup.find(class_='article')

        if not content:
            log.error('content extraction failed')
            print('content extraction failed')
            log.error('{}'.format(page_name))
            raise Exception
        else:
            print(' Content:=')
            print('  size: {}'.format(len(content)))        
            year, month = self.extract_year_month(page_name, soup)
            log.info('year, month = {}, {}'.format(year, month))

            print('  year/month: {}/{}'.format(year, month))
            m = re.search('{}\/.*\/([^\/]+).html'.format(self.ROOT_URL), page_name)
            if m:
                log.debug(pformat(m))
                name = m.group(1)
            else:
                uid_ += 1
                name = '{}'.format(uid_)

            log.debug(content)
            paras = content.findAll('p')  ; log.debug(pformat(paras))

            path_suffix = '{}/{}/{}.txt'.format(year, month, name)

            page_content  = '\n'.join(p.text for p in paras)
            page_abstract = paras[0].text
            title         = soup.find(class_='headline')
            record        = '{}|{}'.format(path_suffix, title.text)

            log.info(title.text)

            return (path_suffix,
                    record, 
                    {
                        self.ARTICLES_DIR : page_content
                        , self.ABSTRACTS_DIR: page_abstract
                    }
            )


if __name__ == '__main__':
    crawler = ViduthalaiCrawler('viduthalai.in')
    crawler.initialize_dir_structure()
    crawler.crawl()
