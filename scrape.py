# Scrape the UCPD archive of incident reports

import requests
from bs4 import BeautifulSoup
import re
import os
import os.path
import urllib.parse
import shutil
import getpass
import argparse
import time
import csv


ARCHIVE_URL = 'https://incidentreports.uchicago.edu/incidentReportArchive.php?startDate=07%2F01%2F2010&endDate={}%2F{}%2F{}'
BASE_URL = 'https://incidentreports.uchicago.edu/'
START_DATE = '07/01/2010'

'''
Every Monday through Friday (except holidays) the University of Chicago Police 
Department posts daily crime incidents and fire incidents that were reported to 
the UCPD over the previous 24 hours. Weekend incident reports (Friday, Saturday, 
and Sunday) are added on the following Monday. The UCPD patrol area includes 
the area between 37th and 64th streets and Cottage Grove Avenue to Lake Shore 
Drive (not including Jackson Park).
'''

# <li class="page-count"><span style="width:50px; border:none; color:#800;">1 / 1663 </span></li>
# <li class="next "><a href="incidentReportArchive.php?startDate=1277960400&amp;endDate=1475470800&amp;offset=5">Next <span aria-hidden="true">→</span></a></li>
# <input class="ss-date hasDatepicker" value="07/10/2010" type="text" name="startDate" id="start-date">

def seed_csv(soup, filename):
    '''
    '''
    table = soup.find('table', attrs = {'class': 'ucpd'})

    col_names = []
    template = table.find('thead')
    for col in template.findAll('th'):
        col_names.append(col.text)

    with open(filename, 'w') as f:
        writer = csv.writer(f)
        writer.writerow(col_names)

    return(table)


def scrape_n_pages(filename, num_pages):
    '''
    '''
    # Get current date information
    cur_day = time.strftime('%A') # Not used yet
    cur_date = time.strftime('%m/%d/%Y')
    cur_month, cur_day, cur_year = cur_date.split('/')
    
    sesh = requests.Session()
    init_page = sesh.get(ARCHIVE_URL.format(cur_month, cur_day, cur_year))
    soup = BeautifulSoup(init_page.content, 'html.parser')
    table = seed_csv(soup, filename)

    num_scraped = 0
    while num_scraped < num_pages:
        scrape_cur_page(filename, table)
        num_scraped += 1   
        next_tag = soup.find('li', attrs = {'class': 'next'})
        if next_tag:
            next_url = urllib.parse.urljoin(BASE_URL, next_tag.find('a')['href'])
            next_page = sesh.get(next_url)
            soup = BeautifulSoup(next_page.content, 'html.parser')
            table = soup.find('table', attrs = {'class':'ucpd'})
        else:
            print('No more incidents reports left after {} pages scraped, terminating scraping')
            break


def scrape_cur_page(filename, table):
    '''
    '''
    csv_rows = []
    incidents = table.find('tbody').findAll('tr')
    for incident in incidents:
        row = []
        for info in incident.findAll('td'):
            row.append((info.text).strip())
        csv_rows.append(row)

    with open(filename, 'a') as f:
        writer = csv.writer(f)
        for row in csv_rows:
            writer.writerow(row)
    print('{} Incidents written to {}\n'.format(len(csv_rows), filename))


if __name__ == '__main__':
    pass



