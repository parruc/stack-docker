from datetime import datetime
import json
import re
import time

from bs4 import BeautifulSoup
import requests

ISMEA_STRUCTURE = {
    'ortofrutta':
        ['ortaggi',
         'frutta',
         'agrumi',
         'frutta-in-guscio'],
    'carni':
        ['carne-bovina',
         'carne-suina-salumi',
         'avicoli-uova',
         'ovicaprini',
         'conigli'],
    'lattiero-caseari':
        ['latte-derivati-bovini',
         'latte-derivati-ovicaprini'],
    'olio-oliva': [],
    'seminativi':
        ['cereali',
         'semi-oleosi'],
    'vino': [],
    'fiori-piante': [],
    'tipici-bio':
        ['prodotti-tipici',
         'prodotti-bio'],
    'pesca': []
}

BASE_URL = "http://www.ismeamercati.it"


def get_iso_date(date):
    return datetime.strptime(date.text, '%d-%m-%y').isoformat()


def get_product(names):
    results = []
    for name in names.text.split(" - ", 2):
        name = name.strip()
        if name not in ["ns", "n.s."]:
            results.append(name)
        else:
            results.append("")
    return results


def get_price(price):
    pric, prty = price.text.strip().split(" ", 1)
    return float(pric.replace(",", ".")), prty.replace("€/", "")


def scrape(url):
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    rows = soup.find_all("tr", re.compile("(odd|even)"))
    for row in rows:
        res = {}
        cols = row.find_all("td")
        res['place'] = row.find("th").text
        res['date'] = get_iso_date(cols[0])
        res['prod'], res['prod_type'], res['prod_qual'] = get_product(cols[1])
        res['price'], res['price_type'] = get_price(cols[2])
        yield res


def scrape_category(category, subcategory):
    results = []
    url = "/".join((BASE_URL, category))
    if subcategory:
        url = "/".join((url, subcategory))
    for result in scrape(url):
        result["cat"] = category
        result["subcat"] = subcategory
        results.append(json.dumps(result))
    return results


results = []
for category, subcategories in ISMEA_STRUCTURE.items():
    if subcategories:
        for subcategory in subcategories:
            results += scrape_category(category, subcategory)
    else:
        results += scrape_category(category, "")

datestr = time.strftime("%Y%m%d")
with open("/var/scrapers/output/ismea_%s.json" % datestr, "w") as out_file:
    out_file.write("\n".join(results))
    print("{} succesfully imported {:d} products".format(datestr, len(results)))
