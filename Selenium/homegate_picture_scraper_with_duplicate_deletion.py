from basic_selenium_browser import create_browser
from simple_duplicate_check import check_for_duplicate_images

from selenium.webdriver.common.keys import Keys

import time
import requests
import os, glob


def download_image(link, img_dir, i, existing_images) -> bool:

    """given multiple links, try to download image files from these links
    
    Parameters:
    link            (string):   url to the image
    img_dir         (string):   directory where the images should be saved
    i               (integer):  amount of images in link list
    existing_images (list):     collected items from image search 

    Returns:
    bool
    """
    underscore_link = link.replace('.','_').replace('/','-').replace(':','#')

    # add timestamp to vary between pictures from different days and url at the end
    image_path = img_dir+f'{underscore_link}_picture_{i}.jpg'


    if image_path not in existing_images:

        with open(image_path, 'wb') as f:

            # take pic from pic list
            request_url = img_urls[i]

            r = requests.get(request_url)
            if r.status_code == 200: 
                f.write(requests.get(request_url).content)

                print(image_path + ' was successfully downloaded.')



            else: 
                print(f'Error. Image {image_path} from URL {img_urls[i]} cannot be retrieved.')
                return False

        return True

    else:
        print(f'Image {image_path} already exists and is skipped')

        return False

if __name__ == '__main__':

    # set img directory
    img_dir = input('EnterYourPreferredDirectoryHere:)')

    # preferences for apartment, can be retrieved by entering filters at homegate
    site = "https://www.homegate.ch/rent/real-estate/zone-zurich-kreis-1/matching-list?"+\
            "an=400&o=dateCreated-desc&loc=geo-cityregion-kreis-2%2Cgeo-cityregion-kreis-3%2C"+\
            "geo-cityregion-kreis-4%2Cgeo-cityregion-kreis-5%2Cgeo-cityregion-kreis-6%2Cgeo-cityregion-kreis-7%2Cgeo-cityregion-kreis-8&ah=2500"

    print(site)

    os.chdir(img_dir)

    existing_images = []

    for file in glob.glob(".jpg"):

        existing_images.append(file)


    ### instantiate headless webdriver when passing True as Argument ###
    browser = create_browser()

    # landing site
    browser.get(site)
    time.sleep(3)

    # scrolling down the page
    elem = browser.find_element_by_tag_name("body")

    no_of_pagedowns = 12 

    while no_of_pagedowns:
        elem.send_keys(Keys.PAGE_DOWN)
        #increase time here in order to make scrolling smoother. old time was 0.2
        time.sleep(0.5)    
        no_of_pagedowns-=1

    #xpath for getting the nth element: https://stackoverflow.com/questions/4117953/get-second-element-text-with-xpath

    # check inside first page, locate the last page and set up the maximum page count as follows
    last_page_elemt = browser.find_element_by_xpath('//nav/a[position()=3]/p')

    last_page = int(last_page_elemt.text.replace('.',''))
    #print(last_page)

    picture_hrefs = {}

    pages_links = []
    pages_links.append(browser.find_element_by_xpath('//nav/a[position()=2]').get_attribute('href'))

    #print(pages_links)

    # for all following pages:
    for i in range(last_page):

        # list of hrefs inside dictionary
        picture_hrefs[f'page {i+1}'] = []

        # add all links
        picture_hrefs[f'page {i+1}'] = [elem.get_attribute('href') for elem in browser.find_elements_by_xpath('//a[@data-test="result-list-item"]')]

        # get href to next page
        next = browser.find_element_by_xpath('//nav/a[position()=2]').get_attribute('href')

        pages_links.append(next)

        # open next page
        browser.get(next)

    for site, links in picture_hrefs.items():

        for link in links:
            ### once on on the apartment / room site ###
            browser.get(link)

            try:

                next_img_btn = browser.find_element_by_xpath('//button[@title="Next image"]')    

                for i in range(10):
                    next_img_btn.click()
                    time.sleep(1)

            except:
                print(f'Only 1 image found for {link}. Skipping this page')
                continue

            # get all image URLs
            site_images = browser.find_elements_by_xpath('//img')

            img_urls = [elem.get_attribute("src") for elem in site_images]

            # clean unwanted files and other content
            img_urls = [image for image in img_urls if '.jpg' in image]

            # remove duplicates
            # unique_images = list(set(image_urls))

            # download all images
            for i in range(len(img_urls)):

                download_image(link, img_dir, i, existing_images)

    
    duplicate_files = check_for_duplicate_images(img_dir)

    # in case one wants to know which duplicates where deleted
    print(duplicate_files)
           
            






