'''
Script to read HTML content from a specific search on the website Liberation.fr

@author: Joao Hatum
@date: 07Dec2017
'''

# pylint: disable=invalid-name

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

def get_page_content(request_url):
    """Requests a specific page and returns the HTML tree."""
    page = requests.get(request_url)
    parser = lmxhtml.HTMLParser(encoding=page.encoding)
    return lmxhtml.fromstring(page.content, parser=parser)

def from_list_to_str(input_list):
    """Converts a list to a simple string"""
    final_str = ""
    for list_item in input_list:
        final_str += to_utf8(list_item)

    return final_str

def to_utf8(string):
    """Converts a string to UTF-8"""
    return str(string.encode('utf-8'))

# Since the page may use ajax requests for paging, we should search in smaller
# periods
CURRENT_DATE = datetime.date(2014, 3, 1)
END_DATE = datetime.date(2017, 7, 31)

MAIN_URL = 'http://liberation.fr'
KEYWORDS = {'lula': False, 'dilma rousseff': False, 'michel temer': False, \
    'sergio moro': False, 'odebrecht': False, 'petrobras': False}
dates = []
titles = []
urls = []
keywords_in_articles = []

final_elements = []

# Read HTML content
while CURRENT_DATE != END_DATE:
    authors = []
    next_date = add_month(CURRENT_DATE)
    if next_date > END_DATE:
        next_date = END_DATE
    tree = get_page_content('http://www.liberation.fr/recherche/?sort=-publication_date' + \
        '_time&q=lava+jato&period=custom&period_start_day=%d&period_start_month=%d&' % \
        (CURRENT_DATE.day, CURRENT_DATE.month) +\
        'period_start_year=%d&period_end_day=%d&period_end_month=%d&period_end_year=%d&' %\
         (CURRENT_DATE.year, next_date.day, next_date.month, next_date.year) +\
        'editorial_source=&paper_channel=')

    # Reading dates, titles and URLs
    dates = tree.xpath('//p[@class="live-datetime"]/a/text()')
    titles = tree.xpath('//h3[@class="live-title"]/a/text()')
    urls = tree.xpath('//h3[@class="live-title"]/a/@href')

    for url in urls:
        tree = get_page_content(MAIN_URL+url)

        # Retrieving the author from each URL.
        searched_authors = tree.xpath('//span[@class="author"]/a/span/text()')
        if searched_authors:
            authors.append(searched_authors[0])
        else:
            authors.append('')

        # Checking if the keywords appear on each URL.
        article_body = tree.xpath('//div[@class="article-body read-left-padding"]/p/text()')
        article_body = from_list_to_str(article_body)
        current_keywords = KEYWORDS
        for key, val in current_keywords.items():
            if key in str.lower(article_body):
                current_keywords[key] = True
        keywords_in_articles.append(current_keywords)

    # Adding all the info to the final content array.
    for i, val in enumerate(titles):
        line_tuple = (dates[i], titles[i], MAIN_URL+urls[i], authors[i])
        for key, dict_val in keywords_in_articles[i].items():
            line_tuple += (dict_val,)
        final_elements.append(line_tuple)
    CURRENT_DATE = next_date

# Write to CSV file
with open('liberation.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=';', \
        quotechar='|', quoting=csv.QUOTE_MINIMAL)

    header = ["Data", "Titulo", "URL", "Autor"]
    for key, val in KEYWORDS.items():
        header.append(str.upper(to_utf8(key)))

    writer.writerow(header)
    for item in final_elements:
        writer.writerow([item[0], item[1], item[2], item[3], item[4], \
            item[5], item[6], item[7], item[8], item[9]])
