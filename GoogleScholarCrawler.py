from selenium import webdriver
import pandas as pd
import numpy as np
import time
import datetime
import subprocess
import re
import os
import requests

author = "Nico Zheng"
email = "nico921113[at]gmail.com"

keywords = ["wikipedia"]  # search keywords
journals = ['information systems research', 'mis quarterly', 'journal of management information systems',
 'journal of the association for information systems', 'management science', 'operational research']
fpath = "/Users/Nico/test/test_googlecrawer"   # output file folder

alias = {'information systems research':"ISR", 'mis quarterly':'MISQ', 'journal of management information systems':"JMIS",
         'journal of the association for information systems':"JAIS", 'management science':'MS', 'operational research':"OR"}

'''
crawl google scholar search results and save pdf if the file was avaliable.

requirements:
    - selenium  `pip install selenium`
    - webdriver `brew install webdriver`
    - requests `pip install requests`

will create local file folders based on keywords and journal as following:
$ tree test_googlecrawer -d
test_googlecrawer
└── wikipedia
    ├── information\ systems\ research
    ├── journal\ of\ management\ information\ systems
    ├── journal\ of\ the\ association\ for\ information\ systems
    ├── management\ science
    ├── mis\ quarterly
    └── operational\ research

in each folder, there is a log file recorded detailed search results (author, title, journal, year and whether pdf is avaliable)
also avaliable pdf files.
the pdf file renamed as:
author-year-title-journal.pdf
'''

## global functions
def downloadPdf(output, link):
    response = requests.get(link)
    with open(output, 'wb') as f:
        f.write(response.content)


def parse(infobox):
    infobox = infobox.lower().split("-")
    infobox = [c.strip() for c in infobox]
    author = infobox[0].split(",")[0]
    journal = infobox[1].split(",")[0]
    year = infobox[1].split(",")[1].strip()
    return author, journal, year

class Article:
    def __init__(self, keywords, target_journal, folder):
        self.keywords = keywords
        self.target_journal = target_journal
        self.output_folder = folder
        self.create_folder()
        self.total_article = {}

    def create_folder(self):
        self.output_fpath = "/".join([self.output_folder, self.keywords, self.target_journal])
        if not os.path.exists(self.output_fpath):
            os.makedirs(self.output_fpath)
            print('created folder {0}'.format(self.output_fpath))

    def getInfo(self, article, driver):
        default = {"title": "NA", "author": "NA", "journal": "NA", "year":"NA", "log": "NA"}
        default['title'] = article.find_element_by_class_name("gs_rt").text.lower()
        default['title'] = re.sub("[^a-z0-9 ]", "", default['title'])
        infobox = article.find_element_by_class_name("gs_a").text
        default['author'], default['journal'], default['year'] = parse(infobox)
        return default

    def getPdf(self, article, driver):
        tmp = article.find_element_by_css_selector("div[class=gs_or_ggsm")
        pdf_link = tmp.find_element_by_tag_name("a").get_attribute("href")
        return pdf_link

    def getFileName(self, alias=alias):
        by = ["author", "year", "title", "journal"]
        if alias:
            if self.info['journal'] in alias.keys():
                self.info['journal-short'] = alias[self.info['journal']]
                by = ["author", "year", "title", "journal-short"]
        if len(self.info['title'].split(" ")) > 10:
            self.info['title-short'] = " ".join(self.info['title'].split(" ")[:10])
            if "journal-short" in self.info.keys():
                by = ["author", "year", "title-short", "journal-short"]
            else:
                by = ["author", "year", "title-short", "journal"]
        filename = "-".join([self.info[c] for c in by]) + ".pdf"
        return filename

    def fit(self, article, driver, num):
        try:
            self.info = self.getInfo(article, driver)
        except:
            print("article info parse error!")
            self.info = None
        if self.info:
            try:
                self.pdf = self.getPdf(article, driver)
            except:
                self.info['log'] = "pdf missing"
                self.pdf = None
            if self.pdf:
                self.filename = self.getFileName()
                output = self.output_fpath + "/" + self.filename
                try:
                    downloadPdf(output, self.pdf)
                except:
                    self.log = self.info['log'] + "||| pdf download error"
        self.total_article[num] = self.info

def run(keywords, journals, recursive = 6):
    '''
    search based on keywords and journals combinations
    recursive is the number of request pages.
    '''
    driver = webdriver.Chrome()
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    driver.get('https://scholar.google.com/')
    for i in keywords:
        for j in journals:
            cnt = 1
            articles = Article(i, j, fpath)
            search_keyword = " ".join([i.lower(), '''source:"{}"'''.format(j.lower())])
            print("current search key: {0}".format(search_keyword))
            input_element = driver.find_element_by_name("q")
            input_element.clear()
            input_element.send_keys(search_keyword)
            input_element.submit()
            time.sleep(2)
            for n in range(recursive):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                elements = driver.find_elements_by_css_selector("div[class=gs_r\ gs_or\ gs_scl]")
                for e in elements:
                    try:
                        articles.fit(e, driver, cnt)
                    except:
                        print("page {} number {} parse error!".format(n, cnt))
                    cnt += 1
                try:
                    driver.find_element_by_css_selector("span[class=gs_ico\ gs_ico_nav_next]").click()
                    time.sleep(5)
                except:
                    pass
            log = pd.DataFrame(articles.total_article).T
            now = datetime.datetime.now()
            log.to_csv(articles.output_fpath+"/"+"logfile_{}.txt".format(now.strftime("%m-%d-%Y")), sep="\t")
    driver.quit()

if __name__ == '__main__':
    run(keywords, journals, recursive=6)
