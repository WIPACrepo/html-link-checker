import os
import logging

import requests
from bs4 import BeautifulSoup

def uniform(domain, page, link):
    if link.startswith('mailto:'):
        return link
    if link.startswith('http'):
        return link
    elif link.startswith('/'):
        return domain+link
    else:
        return os.path.join(os.path.dirname(page),link)


checked = set()
def crawl(domain, page, depth=100):
    if page in checked:
        return
    if depth <= 0:
        logging.warning('depth limit hit on %s', page)
        return

    logging.info('checking %r', page)
    r = requests.get(page)
    checked.add(page)
    if r.status_code in (401,403):
        return # ok, but need auth
    r.raise_for_status()        

    if page.startswith(domain) and 'html' in r.headers['Content-Type']:
        # spider into page
        soup = BeautifulSoup(r.text, 'html.parser')
        for tag in soup.find_all('a'):
            try:
                link = uniform(domain, page, tag['href'])
                if link.startswith('mailto:'):
                    continue
            except Exception:
                logging.warning('error processing `a` tag', exc_info=True)
            else:
                try:
                    crawl(domain, link, depth-1)
                except Exception:
                    logging.info('',exc_info=True)
                    logging.error('bad link: %r -> %r', page, link)
        search = [
            ('link', 'href'),
            ('script', 'src'),
            ('img', 'src'),
            ('iframe', 'src'),
        ]
        for name,attr in search:
            for tag in soup.find_all(name):
                if attr not in tag:
                    continue
                try:
                    link = uniform(domain, page, tag[attr])
                except Exception:
                    logging.info('',exc_info=True)
                    logging.warning('error processing `%s` tag', name)
                else:
                    if link not in checked:
                        try:
                            logging.info('checking %r', link)
                            r = requests.get(link)
                            checked.add(link)
                            r.raise_for_status()
                        except Exception:
                            logging.error('bad link: %r -> %r', page, link)

def main():
    import argparse
    parser = argparse.ArgumentParser(description='Crawl a website for bad links')
    parser.add_argument('--debug',default=False,action='store_true',help='debug logging')
    parser.add_argument('site', nargs=1, help='site basename / home page')
    args = parser.parse_args()

    logformat = '%(asctime)s %(levelname)s %(name)s : %(message)s'
    if args.debug:
        logging.basicConfig(level=logging.INFO, format=logformat)
    else:
        logging.basicConfig(level=logging.WARNING, format=logformat)

    crawl(args.site[0], args.site[0])

if __name__ == '__main__':
    main()
