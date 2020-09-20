from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re
import urllib
import time
#from selenium.webdriver.support.ui import Select

#create a webdriver object and set options for headless browsing
options = Options()
options.headless = True
driver = webdriver.Chrome('./chromedriver',options=options)

#uses webdriver object to execute javascript code and get dynamically loaded webcontent
def get_js_soup(dirpage,url,driver):
    driver.get(url)
    if(dirpage==1):
    #    sel = driver.find_element_by_xpath('//*[@id="edit-items-per-page"]/option[2]')
     #   sel.__setattr__('outerHTML','<option value="10">10</option>')
     #   sel1 = driver.find_element_by_xpath('//*[@id="edit-items-per-page"]/option[6]')
     #   sel1.__setattr__('outerHTML', '<option value="- All -" selected="selected">- All -</option>')

      #  driver.execute_script('sel.__setattr__("outerHTML","<option value="10">10</option>")')
       # driver.execute_script('sel1.__setattr__("outerHTML", "<option value="- All -" selected="selected">- All -</option>")')

       # driver.find_element_by_xpath('//*[@id="edit-submit-customized-directory-search"]').click()
     # temp = Select(driver.find_element_by_xpath('//*[@id="edit-items-per-page"]')).select_by_visible_text('-All-')
        res_html = driver.execute_script('return document.body.innerHTML')
    else:
       res_html = driver.execute_script('return document.body.innerHTML')
    soup = BeautifulSoup(res_html,'html.parser') #beautiful soup object to be used for parsing html content
    return soup

#tidies extracted text
def process_bio(bio):
    bio = bio.encode('ascii',errors='ignore').decode('utf-8')       #removes non-ascii characters
    bio = re.sub('\s+',' ',bio)       #repalces repeated whitespace characters with single space
    return bio

''' More tidying
Sometimes the text extracted HTML webpage may contain javascript code and some style elements. 
This function removes script and style tags from HTML so that extracted text does not contain them.
'''
def remove_script(soup):
    for script in soup(["script", "style"]):
        script.decompose()
    return soup



#extracts all Faculty Profile page urls from the Directory Listing Page
def scrape_dir_page(dir_url,driver):
    print ('-'*20,'Scraping directory page','-'*20)
    faculty_links = []
    faculty_base_url =  'https://cci.uncc.edu/'
    dirpage = 1
    #execute js on webpage to load faculty listings on webpage and get ready to parse the loaded HTML
    soup = get_js_soup(dirpage,dir_url,driver)

  #  for link_holder in soup.find_all('div',class_='name'): #get list of all <div> of class 'name'
    for link_holder in soup.find_all('p',class_= ''):  # get list of all <div> of class 'name'
            for link_holder2 in link_holder.find_all('a'):
                if (len (link_holder2.get_text(strip=True)) != 0):
                    rel_link = link_holder2['href'] #get url
     #   faculty_links.append(faculty_base_url+rel_link)
                    if (rel_link[0:4] == 'http'):
                        faculty_links.append(rel_link)
                    else:
                        faculty_links.append(faculty_base_url+rel_link)
    print ('-'*20,'Found {} faculty profile urls'.format(len(faculty_links)),'-'*20)
    return faculty_links

dir_url = 'https://cci.uncc.edu/directory/sis/faculty' #url of directory listings of CS faculty

faculty_links = scrape_dir_page(dir_url,driver)

def scrape_faculty_page(fac_url,driver):
    #soup = get_js_soup(fac_url,driver)
  #  bio_url = ''
    bio = ''
    dirpage=0
    bio_soup = remove_script(get_js_soup(dirpage,fac_url, driver))
    bio = process_bio(bio_soup.get_text(separator=' '))
    return fac_url,bio

#Scrape homepages of all urls
bio_urls, bios = [],[]
tot_urls = len(faculty_links)
for i,link in enumerate(faculty_links):
    print ('-'*20,'Scraping faculty url {}/{}'.format(i+1,tot_urls),'-'*20)
  #  if(link != 'https://webpages.uncc.edu/richter/' ):
    bio_url,bio = scrape_faculty_page(link,driver)
    if bio.strip()!= '' and bio_url.strip()!='':
       bio_urls.append(bio_url.strip())
       bios.append(bio)
driver.close()

def write_lst(lst,file_):
    with open(file_,'w') as f:
        for l in lst:
            f.write(l)
            f.write('\n')


bio_urls_file = 'bio_urls.txt'
bios_file = 'bios.txt'
write_lst(bio_urls,bio_urls_file)
write_lst(bios,bios_file)