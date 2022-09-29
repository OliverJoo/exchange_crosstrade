import requests
from bs4 import BeautifulSoup
import re
from oliver_util_package import log_utils
import logging

HEADERS = {'User-Agent': 'application/json;charset=utf-8'}
logger = log_utils.logging.getLogger()

def without_kor(text: str) -> str:
    """
    Removing kor character in text

    :param text:str
    :return: str
    """
    logger.debug(text)
    return re.sub('[가-힣]', '', text).strip()

def crawling_element(url: str, element_name: str) -> str:
    """
    website(url) crawling and return one element

    :param url:str
    :param element_name:str
    :return soup.select_one:str
    """
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    logger.debug(soup)
    return soup.select_one(element_name).text

def crawling_elements(url: str, element_name: str) -> list:
    """
    website(url) crawling and return 1 or more elements

    :param url:str
    :param element_name:str
    :return soup.select:list
    """
    response = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    logger.debug(soup)
    return soup.select(element_name)

