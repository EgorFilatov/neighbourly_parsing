import requests
from bs4 import BeautifulSoup
import csv
import math

main_page_url = 'https://www.neighbourly.co.nz/business/list/building-maintenance/auckland-region/auckland-city'
HEADERS = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.4951.54 Safari/537.36 Edg/101.0.1210.39',
           'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9'}
FILE = 'companies_information.csv'

def get_html(url, parameters=None):
    r = requests.get(url, headers=HEADERS, params=parameters)
    return r.text


def create_csv_file(company_name, information, path):
    with open(path, 'w', encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow(['Company name', 'Industry', 'Business_owners_name', 'Address', 'Phone number', 'Email', 'Website'])
        writer.writerow([company_name, information[0], information[1], information[2], information[3], information[4], information[5]])


def add_to_csv_file(company_name, information, path):
    #print(company_name, len(information))
    with open(path, 'a', encoding='utf8', newline='') as file:
        writer = csv.writer(file, delimiter=';')
        writer.writerow([company_name, information[0], information[1], information[2], information[3], information[4], information[5]])


def get_pages_count(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    pages_count = soup.find('div', class_='neighbourhood-profile list-header').find_all('strong')
    pages_count = int(pages_count[-1].get_text(strip=True)) / int(pages_count[-2].get_text(strip=True))
    pages_count = math.ceil(pages_count)
    return pages_count


def get_companies(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    companies = soup.find_all('div', class_='business-item col-lg-4 col-md-6 col-sm-6 col-xs-12')
    information_about_companies = []
    for el in companies:
        information_about_companies.append({
            'company_name': el.find('p', class_='grid-item-profile-info-title').get_text(strip=True),
            'link': el.find('a', class_='grid-item-profile-info').get('href')
        })
    return information_about_companies

def get_information_about_companies(page_html):
    soup = BeautifulSoup(page_html, 'html.parser')
    industry = soup.find('span', class_='category-names').get_text(strip=True)

    if soup.find('a', class_='user-link'):
        business_owners_name = soup.find('a', class_='user-link').get_text(strip=True)
    else:
        business_owners_name = 'No information about name'

    if soup.find_all('div', class_='side-contact'):
        website = soup.find_all('div', class_='side-contact')[-1].find('a', class_='event-tracking-link').get('href')
    else:
        website = ''

    all_information = soup.find_all('script', type='text/javascript')[-3].get_text(strip=True)
    address = all_information[(all_information.find('"address":') + 11):(all_information.find('"', (all_information.find('"address":') + 11)))]
    phone_number = all_information[(all_information.index('"formatted_phone_number":') + 26):(all_information.find('"', (all_information.index('"formatted_phone_number":') + 26)))]
    email = all_information[(all_information.find('"email":') + 9):(all_information.find('"', (all_information.find('"email":') + 9)))]
    all_information = [industry, business_owners_name, address, phone_number, email, website]
    return all_information


def parsing():
    main_page_html = get_html('https://www.neighbourly.co.nz/business/list/building-maintenance/auckland-region/auckland-city/3')
    companies_list = get_companies(main_page_html)
    pages_count = get_pages_count(main_page_html)

    i = 0
    calc = 0
    for company in companies_list:
        if i == 0:
            company_page_html = get_html(company['link'])
            company_information = get_information_about_companies(company_page_html)
            print(main_page_url)
            create_csv_file(company['company_name'], company_information, FILE)
            i = 1
        else:
            company_page_html = get_html(company['link'])
            company_information = get_information_about_companies(company_page_html)
            print(main_page_url)
            add_to_csv_file(company['company_name'], company_information, FILE)

    current_page = 1
    while current_page < pages_count:
        current_page = current_page + 1
        main_page_html = get_html(main_page_url + '/' + str(current_page))
        companies_list = get_companies(main_page_html)
        for company in companies_list:
            company_page_html = get_html(company['link'])
            company_information = get_information_about_companies(company_page_html)
            print(main_page_url + '/' + str(current_page))
            add_to_csv_file(company['company_name'], company_information, FILE)


parsing()
