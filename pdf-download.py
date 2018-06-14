import os
import requests
import logging
from bs4 import BeautifulSoup
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE = 'http://www.theosociety.org/pasadena/ts/tup-ebooks.htm'
base_ref = 'http://www.theosociety.org/pasadena'

def get_pdf_links():
    res = []
    # get base page
    base = requests.get(BASE)

    # scape links
    soup = BeautifulSoup(base.text, 'lxml')
    links = []
    for link in soup.find_all("a"):
        href = link.get('href')
        if href and href.endswith('.pdf'):

            if href.split('/')[-1] not in os.listdir(os.curdir):
                res.append(href)
            else:
                logger.info(" Skipping --> {}".format(href.split('/')[-1]))
    return res

def download():

    links = get_pdf_links()
    for link in links[:84]:
        link = base_ref + link.strip('..')
        logger.info("Downloading --> {}".format(link))

        # Get pdf
        resp = requests.get(link, stream=True)
        tsize = int(resp.headers.get('content-length', 0))
        name = link.split('/')[-1]

        # write
        with open(name, 'wb') as pdf:
            pbar = tqdm(resp.iter_content(1024), total=tsize, unit='B', unit_scale=True)
            for data in pbar:
                pdf.write(data)
                pbar.update(len(data))

            logger.info(" Saved {}".format(name))


if __name__ == '__main__':
    download()
