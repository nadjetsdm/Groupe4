import time
import random
import re
import os
import logging
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options

DRIVER_PATH = "C:\chromedriver\chromedriver.exe"



# declaring a list, that contains the urls wich we want to be scraped
OBJECT_URLS = [
        'https://www.google.fr/maps/place/CPAM+Paris+12/@48.8370362,2.3885378,16.39z/data=!4m6!3m5!1s0x47e673c30ce76aed:0xb1b2d0f67387fa79!8m2!3d48.837866!4d2.3935733!16s%2Fg%2F11gmfyhp42',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8488736,2.408246,17.65z/data=!4m6!3m5!1s0x47e6727dc5b49d83:0xd898bba56cfb4c83!8m2!3d48.8488849!4d2.4100187!16s%2Fg%2F11bvt68j8d',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8664189,2.3692318,18.47z/data=!4m6!3m5!1s0x47e66de327ce7a33:0xdafde4adc7e1de49!8m2!3d48.8664669!4d2.3709093!16s%2Fg%2F11b6gcxvkl',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8774575,2.3605016,18.86z/data=!4m6!3m5!1s0x47e66e736c68905d:0x16c054264cb3af27!8m2!3d48.8775089!4d2.3616668!16s%2Fg%2F11b7k2sc2c',
        # 'https://www.google.fr/maps/place/CPAM/@48.8850957,2.3846864,19.69z/data=!3m1!5s0x47e66dc5eee18299:0xc299d22c6d1156e8!4m6!3m5!1s0x47e66dc5f1046d3b:0x10d49b2a511a1b6e!8m2!3d48.8851479!4d2.385388!16s%2Fg%2F11bzz69cgw',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8835143,2.3177806,17.86z/data=!4m6!3m5!1s0x47e66fb3b66a322b:0x99afd85505a11a6a!8m2!3d48.8840113!4d2.3201583!16s%2Fg%2F11b6bbzl2x',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8331426,2.3202366,18.22z/data=!4m6!3m5!1s0x47e671b4c2fa1eb1:0x50f439dbdc3c2b5!8m2!3d48.8332528!4d2.3214463!16s%2Fg%2F11ckxxvnx7',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.823332,2.3658472,18.79z/data=!4m6!3m5!1s0x47e67229aa18de37:0xce8352b33b5d5808!8m2!3d48.823046!4d2.3671047!16s%2Fg%2F11bxfzydxx',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8403588,2.3000619,18.53z/data=!4m6!3m5!1s0x47e6703e5f8da9b9:0xa8ce3fbaf1d5238b!8m2!3d48.8406249!4d2.3008405!16s%2Fg%2F11bxg0bfpd',
        # 'https://www.google.fr/maps/place/CPAM+de+Paris/@48.8978312,2.3457322,17.95z/data=!4m6!3m5!1s0x47e66ef535e04a53:0xf8991c933b292901!8m2!3d48.8977825!4d2.3475496!16s%2Fg%2F11cky7bl5_'

           ]

# setting up the logging object
logger = logging.getLogger('main')
logging.basicConfig(
    format='[%(asctime)s] [%(levelname)s] - %(message)s',
    datefmt='%H:%M:%S'
    )



# we can change the logging level. Use logging.DEBUG if necesarry
logger.setLevel(logging.DEBUG)


def scrape_an_object(object_url: str) -> tuple:
    """
    This method will:
    - open the input URL (of a google maps object like stores, hotels, restaurants etc...)
    - accept the cookies
    - get some basic information of the given object (name, address, overall rating, 
      and the number of reviews)
    - scroll down to the bottom of the page in order to load every reviews in the html source code
    - scrape the div that contains the reviews
    args: 
        object_url: the url of the google maps object to open
    
    returns a tuple containing:
        store_main_data: a dictionary containing the basic information of the google map object 
                      (name, address, overall rating, and the number of reviews)
        reviews_source: a bs4 object containing the html source code of the div 
                        that contains all the reviews
    
    """
 # setting the chrome driver for selenium
    driver = webdriver.Chrome(service=Service(DRIVER_PATH))
    chrome_options = Options()
    chrome_options.add_argument("--lang=fr")  # Définir la langue sur le français
    driver = webdriver.Chrome(options=chrome_options)

    # opening the given URL
    logger.debug("Opening the given URL")
    driver.get(object_url)



    # accepting the cookies
    logger.debug("Accepting the cookies")
    driver.find_element(By.CLASS_NAME,"lssxud").click()

    # waiting some random seconds
    time.sleep(random.uniform(10,15))

    # I use CSS selectors where I can, because its more robust than XPATH
    object_name = driver.find_element(
        By.CSS_SELECTOR,
        'h1.DUwDvf.fontHeadlineLarge'
    ).text
    logger.debug(f'Object_name OK : {object_name}')

    object_address = driver.find_element(
        By.CSS_SELECTOR,
        'div.Io6YTe.fontBodyMedium'
    ).text



    logger.debug(f'Object_address OK : {object_address}')


    # for some reason sometimes google full randomly loads the page
    # with a slightly different page structure. to be able to handle this,
    # I created an except branch that scrapes the right objects in that scenario
    try:

        overall_rating = driver.find_element(
            By.CSS_SELECTOR,
            'div.F7nice.mmu3tf'
        ).text.split()[0]
        logger.debug(f'Overall_rating OK : {overall_rating}')

        review_number = driver.find_element(
            By.CSS_SELECTOR,
            'div.F7nice.mmu3tf'
        ).text.replace(' ','')

        review_number = int(re.compile(r'\d+').findall(review_number)[-1])
        logger.debug(f'Review_number OK : {review_number}')

        # click to load further reviews
        driver.find_element(
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span[2]/span[1]/span'
        ).click()

        logger.debug('Clicked to load further reviews')

        time.sleep(random.uniform(0.1, 0.5))


        # find scroll layout
        scrollable_div = driver.find_element(
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]'
        )

        logger.debug('Scroll div OK')


     
    except NoSuchElementException:

        logger.debug('Except branch')

        div_num_rating = driver.find_element(
            By.CSS_SELECTOR,
            'div.F7nice'
        ).text
        overall_rating = div_num_rating.split()[0]
        logger.debug(f'Overall_rating OK : {overall_rating}')

        review_number = int(div_num_rating.split()[1].replace('(','').replace(')',''))
        logger.debug(f'Review_number OK : {review_number}')

        # click on the review tab
        driver.find_element(
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]/div/div/button[2]/div[2]/div[2]'
        ).click()
        logger.debug('clicked to load further reviews')

        time.sleep(random.uniform(0.1, 0.5))

        # find scroll layout
        scrollable_div = driver.find_element(
            By.XPATH,
            '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[3]'
        )
        logger.debug('Scroll div OK')

    time.sleep(random.uniform(2,4))

    # scroll as many times as necessary to load all reviews
    for _ in range(0,(round(review_number/5 - 1)+1)):



        driver.execute_script(
            'arguments[0].scrollTop = arguments[0].scrollHeight',
            scrollable_div
        )
        time.sleep(random.uniform(1, 2))



  # scraping each individual review
    reviews = driver.find_elements(By.CSS_SELECTOR, 'div.MyEned')
    for review in reviews:
        # Clicking on "Plus" to expand the full review text
        try:
            more_button = review.find_element(By.CSS_SELECTOR, 'button.w8nwRe.kyuRq')

            more_button.click()
            time.sleep(random.uniform(1, 2))
        except NoSuchElementException:
            pass


    # parse the html with a bs object
    response = BeautifulSoup(driver.page_source, 'html.parser')
    reviews_source = response.find_all('div', class_= 'jJc9Ad')
    logger.debug('Source code has been parsed!')
    


    # closing the browser
    driver.close()

    # storing the data in a dict
    store_main_data = {'object_name': object_name,
                       'object_address': object_address,
                       'overall_rating': overall_rating,
                       'review_num': review_number,
                       'object_url':object_url}

    return store_main_data, reviews_source



def extract_reviews(reviews_source: list) -> list:

    r"""
    This method processes the input html code and returns a list 
    containing the reviews.
    """

    review_list = []

    logger.debug('Starting iterate trough the reviews...')
    
    users = []
    dates = []
    reviews = []
    review_rating = []

    for review in reviews_source:
        # Clicking on "Plus" to expand the full review text
        try:
            if (review.find('span',class_='wiI7pd')):
                users.append(review.find('div',class_='d4r55'))
                dates.append(review.find('span',class_='rsqaWe') if review.find('div',class_='PIpr3c') is None else review.find('div',class_='PIpr3c'))
                reviews.append('..' if review.find('span',class_='wiI7pd') is None else review.find('span',class_='wiI7pd'))
                review_rating.append(review.find_all('img',class_='hCCjke vzX5Ic'))

        except NoSuchElementException:
            pass


        # extract the relevant informations

         
    word = "src"
    for i in range(len(reviews)) :
        review_list.append({'user':users[i].text.strip(),
                            'date': dates[i].text.strip(),
                            'review_rate':len(review_rating[i]),
                            'review_text': reviews[i].text.strip(),
                            })

    return review_list



def main():

    scraped_data =  []

    # loop trough the urls and calling the necessary functions to populate the empty scraped_data list
    for i, url in enumerate(OBJECT_URLS):
        try:
            time.sleep(random.uniform(3,10))
            
            store_main_data, reviews_source = scrape_an_object(url)
            scraped_data.append(store_main_data)



            review_list = extract_reviews(reviews_source)
            scraped_data[i]['reviews'] = review_list

            if scraped_data[i]['review_num'] != len(scraped_data[i]['reviews']):
                logger.warning(f'For some reason not all the reviews had been scraped for the following object: {store_main_data["object_name"]}')


        except Exception as exception:
            logger.error(f'{url} \n {exception}')

  

            
   
            scraped_data.append(
                    {
                    'object_name': 'Error',
                    'object_address': 'Error',
                    'overall_rating': 'None',
                    'review_num': 'None',
                    'object_url':url,
                    'reviews':[{}]
                    }
                )

        logger.info(f' {i+1} URL has been finished from the total of {len(OBJECT_URLS)}')


    # reading the dict with pandas
    result_df = pd.json_normalize(
                scraped_data,
                record_path = ['reviews'],
                errors='ignore',
                meta=['object_name', 'object_address', 'overall_rating', 'review_num', 'object_url']
                )


    # # # reorder the columns
    # # result_df = result_df[[
    # #             'object_name','object_address','overall_rating','review_num',
    # #             'object_url', 'name','date','review_text'
    # #             ]]

    #Saving the result into an excel file
    SAVING_PATH = "C:/Users/bebel/Documents/Projet_entreprise"
    save_path = os.path.join(SAVING_PATH,'scrape_result.xlsx')
    result_df.to_excel(save_path,index= False)

    logger.info(f'Successfully exported the result file in the following folder: {os.path.join(SAVING_PATH,"scrape_result.xlsx")}')


if __name__ == '__main__':
    main()
