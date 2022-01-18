import requests
from bs4 import BeautifulSoup as soup
import re


class LinkHandler:
    """Also known as the link fondler; this fondles all of the links"""

    def __init__(self):
        self.start_url = None
        self.headers = None

    def navigate_link(self, nagivate_to=None):
        """Try/except block to catch DNS failure/other network failures"""
        # Navigate link attempts to return a https request from input link.
        if nagivate_to is None:
            return None
        try:
            return requests.get(nagivate_to, headers=self.headers)
        except requests.exceptions.RequestException as e:
            raise SystemExit(e)

    def parse_link_request(self, link=None):
        # Use beautiful soup to parse text from web request.
        if link is None:
            return None
        else:
            request = self.navigate_link(link)
        bsoup = soup(request.content, 'html.parser')
        return bsoup.text.replace('"', '')

    @staticmethod
    def get_next_link(text):
        split_text = text.split(',')
        raw_link = split_text[1]
        protocol = re.findall(r'(\w+)://', raw_link)

        if protocol:
            curated_link = raw_link.split('next:')
            curated_link = curated_link[1]
        else:
            print('Could not identify next link.')
            return None
        # raw_link = re.findall(r'next:.*&paginator=cursor', text)

        '''try:
            raw_link = raw_link[0]
        except:
            print('stop')
        link = raw_link.replace('next:', '')
        return link'''
        return curated_link


def generate_request(url, headers=None):
    request = requests.get(url, headers=headers)

    if request:
        return request


def get_data(request):
    bsoup = soup(request.content, 'html.parser')
    if bsoup:
        return bsoup.text
