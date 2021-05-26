import re
import requests
import pandas as pd
from typing import Tuple
from bs4 import BeautifulSoup

def get_twitter_followers(link) -> int:
    
    r = requests.get(link)
    soup = BeautifulSoup(r.content,'lxml')
    
    try:
        f = soup.find('li', class_="ProfileNav-item--followers")
        title = f.find('a')['title']
        # attention for the separator here
        num_followers = int(title.split(' ')[0].replace('.','')) 
    
    except:
        num_followers = 'twitter url yielded nothing'
    
    return num_followers

def get_address(soup) -> str:
    
    address = soup.find('div', attrs ={'class': "_2wzd"}).get_text()
    #begin = "[aA-zZ]+\s[0-9]+" # gets all streetnames with numbers
    #end = "[0-9]+\s[a-zA-ZäöüÄÖÜß]+" # postcode and city name (Umlaute because of DE/AT/CH)
    address = re.sub("[\(\[].*?[\)\]]", "", address)
    address = address.replace('  ',', ')

    # ATTENTION! this does not work for street names with hyphens
    #result_beg = re.findall(begin,address)
    #result_end = re.findall(end,address)
    #address = result_beg[0]+', '+result_end[0]
    return address

def get_phone_number(soup) -> str:
    # this html classes text still seems to contain both address and phone number
    phone_number = soup.find('div', attrs ={'class':"_4-u2 _u9q _3xaf _4-u8"}).get_text()
    #finds '+43 6452 4033360', '+41 27 603 40 00' or '089 72014342'
    # does not work for US numbers (yet), they are in format +1-123-456-789 typically
    phone_regex = re.findall("[0]+.[0-9]+.[0-9]+|[\+0-9]+\s[0-9]"+\
        "+\s[0-9]+\s[0-9]+\s[0-9]+|[\+0-9]+\s[0-9]+\s[0-9]+",phone_number)
    #print('content from phone_number',phone_regex) # beware, this is a list!
    # remove short matches such as '0 8008' from addresses that are found inside here
    phone_sane = [i for i in phone_regex if len(i) >7] #POSSIBLY missing some phone_numbers, check again
    tel = phone_sane[0].replace(" ","").replace('-','').replace('(0)','').replace(")",'').replace("(","")

    return tel

def scrape_likes(fb_url) -> Tuple[int, str, str]: 
    
    fb_likes = 0
    response = requests.get(fb_url)
    soup = BeautifulSoup(response.content,'lxml')
    #print('soup is',soup)
    f = soup.find('div', attrs={'class': '_4-u3 _5sqi _5sqk'})
    
    try:
        # find span tag inside class
        likes=f.find('span',attrs={'class':'_52id _50f5 _50f7'}) 
        # find numbers separated by 2 pts
        x= re.findall("[0-9]+.[0-9]+.[0-9]+|[0-9]+",likes.text) 

        # change line to x[0].replace(',','') when using a non-german IP
        # only german site uses '.' as separator
        x[0]=x[0].replace('.','') 

        fb_likes = int(x[0])

        # getting tel or address might fail
        try:
            tel = get_phone_number(soup)
        except:
            tel = None
        try:
            address = get_address(soup)
        except:
            address = None
        
    except:
        fb_likes = 'fb url did not work'
        tel = None
        address = None
        
    return fb_likes, tel, address

def scrape_site(url) -> object:

    soup = BeautifulSoup(requests.get(url).content,'lxml')
    links = [link.get('href') for link in soup.find_all('a')]

    #sites can be extended by '(at)' regex
    # list of strings to search for
    sites = ['facebook.com', 'twitter.com', 'linkedin.com','@'] 
    links_sane = [i for i in links if i]
    
    #create list with matched strings
    try:
        new_links = [l for l in links_sane for s in sites if s in l]
    except:
        print('No usable link detected.'+\
            ' life is beautiful but you have to continue with another one')
  
    facebook = [i for i in new_links if sites[0] in i]

    facebook = [i for i in facebook if not 'sharer' in i]
    
    twitter = [i for i in new_links if sites[1] in i]
    twitter = [i for i in twitter if not len(i)>50]
    
    linkedin = [i for i in new_links if sites[2] in i]
    linkedin = [i for i in linkedin if not 'share' in i]
    
    email = [i for i in new_links if sites[3] in i]
    email = [i.replace('mailto:','') for i in email]
    
    if twitter:
        # num_followers
        num_followers = get_twitter_followers(twitter[0])

    else:

        twitter = [None]
        num_followers = None
        
    if facebook:
        # returns fb_likes, tel, address
        fb_likes,tel,address = scrape_likes(facebook[0]) 

    else:
        # set all to None
        facebook = [None]
        fb_likes = None
        tel = None
        address = None
        
    if email:

        if type(email)==list:

            email = email[0]

        else:
            email = email
    else:
        email = None
        
    if linkedin:
        linkedinurl = linkedin[0]
    else:
        linkedinurl = None
    
    # DataFrame structure from retrieved data
    df = pd.DataFrame(columns=['fb_likes','twitter_followers',
                                'tel','url','fb_url','address',
                                'twitter_url','email','linkedin'])
    
    try:
        # better formatting for search in SF
        url = url.replace('https://','').replace('http://','') 

        if(url.endswith('/')):
            url=url[:-1]
        stuff = [fb_likes,num_followers,tel,url,facebook[0],
                    address,twitter[0],email,linkedinurl]
        
        # displays entire columns, change second parameter to char length
        pd.set_option('display.max_colwidth', -1)
        
        df = df.append(pd.Series(stuff,index=df.columns),ignore_index=True)
        
        print(facebook[0])
        if linkedin:
            print(linkedin[0])
        
    except:

        print('no stuff for',url)

    return df
       
                 
# example function call
df = scrape_site(input("Enter URL:"))