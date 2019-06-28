import re
from typing import List

import requests
from bs4 import BeautifulSoup

PHONE_NUMBER_REGEXP = '[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'


class PhoneNumberScraper:
    def __init__(self, url: str, contact_page_paths: List[str]):
        self.url = url
        self.contact_page_paths = contact_page_paths
        self.soup = None

    def fetch_soup(self, url: str):
        response = requests.get(url).content
        self.soup = BeautifulSoup(response, 'html.parser')

    def remove_unwanted_tags(self):
        for unwanted_tag in self.soup(['script', 'style']):
            unwanted_tag.extract()

    def fetch_phone_numbers(self) -> List[str]:
        return self.soup.find_all(string=re.compile(PHONE_NUMBER_REGEXP))

    def extract_phone_numbers(self, contact_page_url: str) -> List[str]:
        self.fetch_soup(contact_page_url)
        self.remove_unwanted_tags()
        numbers = self.fetch_phone_numbers()
        return self.prepare_numbers(numbers)

    def scrape_phone_numbers(self) -> List[str]:
        if not self.contact_page_paths:
            return self.extract_phone_numbers(self.url)
        else:
            return [
                number
                for contact_page_path in self.contact_page_paths
                for number in self.extract_phone_numbers(f'{self.url}/{contact_page_path}')
            ]

    @staticmethod
    def prepare_numbers(numbers: List[str]) -> List[str]:
        return [''.join(char for char in number if char.isdigit()) for number in numbers]
