import re, os 
import time 
import requests
import datetime
import pandas as pd
from bs4 import BeautifulSoup


def file_wd():
    abspath = os.path.abspath(__file__)
    dname = os.path.dirname(abspath)
    os.chdir(dname)

def get_twitter_followers(link):
    
    r = requests.get(link)
    soup = BeautifulSoup(r.content,features="lxml")
    
    try:
        f = soup.find('li', class_="ProfileNav-item--followers")
        title = f.find('a')['title']
        num_followers = int(title.split(' ')[0].replace('.','')) #attention for the separator here as well
    
    except:
        num_followers = 'twitter url yielded nothing'
    
    return num_followers

def get_address(soup):
    
    address = soup.find('div', attrs ={'class': "_2wzd"}).get_text()

    address = re.sub("[\(\[].*?[\)\]]", "", address)
    address = address.replace('  ',', ')

    #ATTENTION! this does not work for street names with hyphens, from e.g. https://www.facebook.com/dhlconsulting/ 

    return address

def get_phone_number(soup):
    #this class still seems to be all info, meaning address and phone number are mixed together here
    phone_number = soup.find('div', attrs ={'class':"_4-u2 _u9q _3xaf _4-u8"}).get_text()
    #finds '+43 6452 4033360', '+41 27 603 40 00' or '089 72014342'
    #does not work for US numbers, they are in format +1-123-456-789 typically
    phone_regex = re.findall("[0]+.[0-9]+.[0-9]+|[\+0-9]+\s[0-9]+\s[0-9]+\s[0-9]+\s[0-9]+|[\+0-9]+\s[0-9]+\s[0-9]+",phone_number)

    #remove short matches such as '0 8008' from addresses that are found inside here
    phone_sane = [i for i in phone_regex if len(i) >7] #POSSIBLY missing some phone_numbers, check again
    tel = phone_sane[0].replace(" ","").replace('-','').replace('(0)','').replace(")",'').replace("(","")
    return tel

def scrape_likes(fb_url): 
    
    fb_likes = 0
    response = requests.get(fb_url)
    soup = BeautifulSoup(response.content,'lxml')
    f = soup.find('div', attrs={'class': '_4-u3 _5sqi _5sqk'})
    
    try:
        likes=f.find('span',attrs={'class':'_52id _50f5 _50f7'}) #finding span tag inside class
        #print(likes)
        x= re.findall("[0-9]+.[0-9]+.[0-9]+|[0-9]+",likes.text) #adapted regex to find numbers separated by 2 pts

        #change line to x[0].replace(',','') when using a non-german IP. only german site uses '.' as separator
        x[0]=x[0].replace('.','') 

        fb_likes = int(x[0])

        try:
            tel = get_phone_number(soup)
        except:
            tel = None
        try:
            address = get_address(soup)
        except:
            address = None
        
    except:
        fb_likes = 0
        tel = None
        address = None
        
    return fb_likes, tel, address

#maybe add function that searches for imprint impressum on site and also checks info there! not all fb pages have phone numbers
def scrape_site(url): 
    
    new_links = []
    site = url
    try:
        cont = requests.get(site,timeout=5)

        soup = BeautifulSoup(cont.content,'lxml')
        links = [link.get('href') for link in soup.find_all('a')]


        sites = ['facebook.com', 'twitter.com', 'linkedin.com','@'] #list of strings to search for, removed instagram
        links_sane = [i for i in links if i]
        
        #create list with matched strings
        try:
            new_links = [l for l in links_sane for s in sites if s in l]
        except:
            print('No usable link detected. life is beautiful but you have to continue with another one')
        
        facebook = [i for i in new_links if sites[0] in i]
        #print(facebook)  #printing the list to check contents
        facebook = [i for i in facebook if not 'sharer' in i]
        
        twitter = [i for i in new_links if sites[1] in i]
        twitter = [i for i in twitter if not len(i)>50]
        
        linkedin = [i for i in new_links if sites[2] in i]
        linkedin = [i for i in linkedin if not 'share' in i]
        
        email = [i for i in new_links if sites[3] in i]
        email = [i.replace('mailto:','') for i in email]
        email = [i for i in email if len(i)<20]

        if twitter:
            num_followers = get_twitter_followers(twitter[0])

        else:
            twitter = [None]
            num_followers = None
            
        if facebook:
            fb_likes,tel,address = scrape_likes(facebook[0]) #returns fb_likes, tel, address

        else:
            facebook = [None]
            fb_likes = 0
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
        
        try:

            url = site.replace('https://','').replace('http://','') #better formatting for search in SF
            if(url.endswith('/')):
                url=url[:-1]

            stuff = [fb_likes,num_followers,tel,url,facebook[0],address,twitter[0],email,linkedinurl]

        except:
            print('no data for',url)

    except:
        print('Timeout for:',site)
        stuff = ([0] + [None] + [None] + [site] + ([None] * 5))

    return stuff        

def import_companies_export_all(file):

    df = pd.DataFrame(columns=['fb_likes','twitter_followers','tel','url','fb_url','address','twitter_url','email','linkedin'])
    pd.set_option('display.max_colwidth', 60)

    with open(file) as f:
        lines = [line.rstrip() for line in f]

    for i in lines:
        df = df.append(pd.Series(scrape_site(i),index=df.columns),ignore_index=True)

        time.sleep(0.1)


    df2 = df.sort_values(by=['fb_likes'], ascending=False) 
    print('amount companies screened:',len(df2.index))

    df2.to_csv(f'{datetime.datetime.now():%Y%m%dT%H%M%SZ}companies.csv',index=False)

file_wd()
import_companies_export_all('url_test.csv')

