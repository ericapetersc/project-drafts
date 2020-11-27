import re
import requests
import logging
import html.parser
from time import sleep
from bs4 import BeautifulSoup

URL = 'https://www6g.senado.leg.br/transparencia/sen/5008/?ano=2020'

logging.basicConfig(level="INFO")
log = logging.getLogger("logger")

def get_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        log.info('Requisição bem sucedida!')
        return BeautifulSoup(response.content, 'html.parser')
    log.exception(f'Erro na requisição com status {response.status_code}')

def get_element_by_id(content, id):
    return content.find(id=id)

def get_table(content):
    return content.find("table")

def get_links(content):
    links = [link['href'] for link in content.find_all('a', href=True)]
    return links

def get_links_from_debit_resources():
    content = get_content(URL)
    content = get_element_by_id(content, 'collapse-ceaps')
    return get_links(get_table(content))

def download_doc_from_link(url):
    
    if 'documento' not in url:
        return

    response = requests.get('https://www6g.senado.leg.br'+url, stream = True)
    number = url.split('documento/', 1)[1]
    
    with open(f"documents/doc_{number}.pdf","wb") as pdf: 
        for chunk in response.iter_content(chunk_size=1024):  
            if chunk: 
                pdf.write(chunk) 
    
    log.info(f'Doc {number} downloaded.')

def main():

    for link in get_links_from_debit_resources():
        url = URL.split('?',1)[0]+link
        content = get_content(url)
        if not content:
            continue
        month_links = get_links(get_table(content))

        for ml in month_links:
            new_url = url.split('?', 1)[0]+ml           
            content = get_content(new_url)
            if not content:
                continue
            doc_links = get_links(get_table(content))
            
            for dl in doc_links:
                download_doc_from_link(dl)

            
if __name__ == '__main__':
    main()