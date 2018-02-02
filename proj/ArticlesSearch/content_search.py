"""
Module to read HTML content from a specific search on the websites
Le Monde, Liberation and Le Figaro

@author: Joao Hatum
@date: 07Dec2017
"""

# pylint: disable=invalid-name

from collections import OrderedDict
import datetime
import csv
import requests
from lxml import html as lmxhtml

def add_month(date):
    """Add one month to a specific date."""
    if date.month == 12:
        final_month = 1
        final_year = date.year + 1
    else:
        final_month = date.month + 1
        final_year = date.year

    return datetime.date(final_year, final_month, 1)

def from_list_to_str(input_list):
    """Converts a list to a simple string"""
    final_str = ""
    for list_item in input_list:
        final_str += str(list_item)

    return final_str

class ContentSearch():
    """Class for content searching in specific sites"""

    def __init__(self, main_url="", search_url="", login_url="", login_data="",\
        keywords=None):
        self.main_url = main_url
        self.search_url = search_url
        self.keywords = keywords
        self.login_url = login_url
        self.login_data = login_data
        self.csrf_token_xpath = None

        # Since the page may use ajax requests for paging, we should search in smaller
        # periods
        self.current_date = datetime.date(2014, 3, 1)
        self.end_date = datetime.date(2017, 7, 31)

        self.final_elements = []
        self.session = None

    def __get_page_content(self, request_url, session=None):
        """Requests a specific page and returns the HTML tree."""
        if session:
            try:
                page = session.get(request_url)
            except requests.exceptions.ConnectionError:
                self.authenticate(self.csrf_token_xpath) # Reconnect if session is lost
                page = session.get(request_url)
        else:
            page = requests.get(request_url)
        parser = lmxhtml.HTMLParser(encoding=page.encoding)
        return lmxhtml.fromstring(page.content, parser=parser)


    def __search_url_content(self, urls, authors_xpath, body_xpaths):
        authors = []
        keywords_in_articles = []
        for url in urls:
            tree = self.__get_page_content(self.main_url+url, self.session)
            # Retrieving the author from each URL.
            searched_authors = tree.xpath(authors_xpath)
            if searched_authors:
                authors.append(searched_authors[0])
            else:
                authors.append('')

            # Checking if the keywords appear on each URL.
            for i in enumerate(body_xpaths):
                try:
                    article_body = tree.xpath(body_xpaths[i[0]])
                    article_body = from_list_to_str(article_body)
                except:
                    pass
                if article_body and len(article_body) > 100:
                    break
            current_keywords = self.keywords.copy()
            for key in current_keywords:
                if key in str.lower(article_body):
                    current_keywords[key] = True
            keywords_in_articles.append(current_keywords)

        return authors, keywords_in_articles

    def authenticate(self, csrf_token_xpath=None):
        """Performs user authentication, needed in some websites"""
        self.csrf_token_xpath = csrf_token_xpath
        if self.csrf_token_xpath:
            tree = self.__get_page_content(self.login_url)
            login_data['connection[_token]'] = tree.xpath(self.csrf_token_xpath)[0].strip()

        self.session = requests.Session()
        self.session.post(self.login_url, self.login_data)

    def run_from_search(self, xpaths, output_file_name):
        """Run the search using a search form request"""
        # Read HTML content
        while self.current_date != self.end_date:
            authors = []
            next_date = add_month(self.current_date)
            if next_date > self.end_date:
                next_date = self.end_date
            tree = self.__get_page_content(self.search_url % (\
                self.current_date.day, self.current_date.month, self.current_date.year, \
                next_date.day, next_date.month, next_date.year))

            # Reading dates, titles and URLs
            dates = tree.xpath(xpaths[0])
            titles = tree.xpath(xpaths[1])
            urls = tree.xpath(xpaths[2])
            keywords_in_articles = []

            authors, keywords_in_articles = \
                self.__search_url_content(urls, xpaths[3], xpaths[4])

            # Adding all the info to the final content array.
            for i in enumerate(titles):
                i_pos = int(i[0])
                line_tuple = (dates[i_pos], titles[i_pos], self.main_url+urls[i_pos],\
                    authors[i_pos])
                for key, dict_val in keywords_in_articles[i_pos].items():
                    line_tuple += (dict_val,)
                self.final_elements.append(line_tuple)
            self.current_date = next_date

        # Write to CSV file
        with open(output_file_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', \
                quotechar='|', quoting=csv.QUOTE_MINIMAL)

            header = ["Data", "Titulo", "URL", "Autor"]
            for key in self.keywords:
                header.append(str.upper(key))

            writer.writerow(header)
            for item in self.final_elements:
                writer.writerow([item[0], item[1], item[2], \
                    item[3], item[4], item[5], item[6], item[7], item[8], item[9]])

    def run_from_input_urls(self, input_file_name, output_file_name, xpaths):
        """Run the search from a list of URLs instead of a form request"""
        input_file = open(input_file_name)
        urls = []
        for line in input_file.readlines():
            urls.append(line.strip())
        authors, keywords_in_articles = \
                self.__search_url_content(urls, \
                    xpaths[0], xpaths[1])

        # Adding all the info to the final content array.
        for i in enumerate(urls):
            i_pos = int(i[0])
            line_tuple = (urls[i_pos],)
            for key, dict_val in keywords_in_articles[i_pos].items():
                line_tuple += (dict_val,)
            self.final_elements.append(line_tuple)

        # Write to CSV file
        with open(output_file_name, 'w') as csvfile:
            writer = csv.writer(csvfile, delimiter=';', \
                quotechar='|', quoting=csv.QUOTE_MINIMAL)

            header = ["URL"]
            for key in self.keywords:
                header.append(str.upper(key))

            writer.writerow(header)
            for item in self.final_elements:
                writer.writerow([item[0], item[1], item[2], \
                    item[3], item[4], item[5], item[6]])

'''
The main intention of this script was to search content for a
"Lava Jato Operation" master's degree thesis.
So, some variables shouls be defined.
'''

lavajato_keywords = \
    OrderedDict([('lula', False), ('dilma rousseff', False), ('temer', False), \
    ('sergio moro', False), ('odebrecht', False), ('petrobras', False)])

# Liberation
search = ContentSearch(
    'http://liberation.fr',
    'http://www.liberation.fr/recherche/?sort=-publication_date' + \
        '_time&q=lava+jato&period=custom&period_start_day=%d&period_start_month=%d&' \
        +\
        'period_start_year=%d&period_end_day=%d&period_end_month=%d&period_end_year=%d&' \
        +\
        'editorial_source=&paper_channel=', lavajato_keywords)
search.run_from_search(['//p[@class="live-datetime"]/a/text()', \
    '//h3[@class="live-title"]/a/text()', '//h3[@class="live-title"]/a/@href', \
    '//span[@class="author"]/a/span/text()', \
    ['//div[@class="article-body read-left-padding"]/p/text()',\
    '//div[@class="article-body article-edito read-left-padding"]/p/text()']], 'liberation.csv')

# Le Monde
login_data = {'connection[mail]':'anita.hoffmann1@gmail.com','connection[password]':'Fairytale123', \
    'connection[stay_connected]':'1'}
search = ContentSearch(login_url='https://secure.lemonde.fr/sfuser/connexion', login_data=login_data, keywords=lavajato_keywords)
search.authenticate('//input[@id="connection__token"]/@value')
search.run_from_input_urls('le_monde_input.txt', 'le_monde.csv',\
    ['//span[@class="fig-content-metas__author"]/text()', \
     ['//div[@id="articleBody"]/*/text()']])

# Le Figaro
login_data = {'name':'anita.hoffmann1@gmail.com','pass':'Fairytale123', 'op':'SE+CONNECTER', \
    'form_build_id':'form-PSX1cUVLptYb_59yz_8mmOiDqYpA8d0efH_ckpow1Y0', \
    'form_id':'fp_user_services_fp_auth_form'}
search = ContentSearch(login_url='https://plus.lefigaro.fr/user', login_data=login_data, keywords=lavajato_keywords)
search.authenticate()
search.run_from_input_urls('le_figaro_input.txt', 'le_figaro.csv',\
    ['//span[@class="fig-content-metas__author"]/text()', \
     ['//article/div[@class="figp-art__content"]/div/p/text()',\
     '//article/div[@class="figp-art__content"]/div[@class="p"]/text()',\
     '//article/div[@class="figp-art__content"]/div/div[@class="p"]/text()',\
     '//article/div/p/text()']])
