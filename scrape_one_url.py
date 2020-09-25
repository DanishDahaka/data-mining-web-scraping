import re
import requests
import pyperclip
import pandas as pd
from bs4 import BeautifulSoup, SoupStrainer
from IPython.display import display
#pip install pandasgui
from pandasgui import show

def get_twitter_followers(link):
    
    r = requests.get(link)
    soup = BeautifulSoup(r.content,'lxml')
    
    try:
        f = soup.find('li', class_="ProfileNav-item--followers")
        title = f.find('a')['title']
        num_followers = int(title.split(' ')[0].replace('.','')) #attention for the separator here as well!
    
    except:
        num_followers = 'twitter url yielded nothing'
    
    return num_followers

def get_address(soup):
    
    address = soup.find('div', attrs ={'class': "_2wzd"}).get_text()
    #print('soup addres is:', address)
    #begin = "[aA-zZ]+\s[0-9]+" #gets all streetnames with numbers
    #end = "[0-9]+\s[a-zA-ZäöüÄÖÜß]+" #postcode and city name (Umlaute because of DE/AT/CH)
    address = re.sub("[\(\[].*?[\)\]]", "", address)
    address = address.replace('  ',', ')
    #print('regex_address is:',address)
    #ATTENTION! this does not work for street names with hyphens, from e.g. https://www.facebook.com/dhlconsulting/ 
    #result_beg = re.findall(begin,address)
    #result_end = re.findall(end,address)
    #address = result_beg[0]+', '+result_end[0]
    return address

def get_phone_number(soup):
    #this class still seems to be all info, meaning address and phone number are mixed together here
    phone_number = soup.find('div', attrs ={'class':"_4-u2 _u9q _3xaf _4-u8"}).get_text()
    #finds '+43 6452 4033360', '+41 27 603 40 00' or '089 72014342'
    #does not work for US numbers (yet), they are in format +1-123-456-789 typically
    phone_regex = re.findall("[0]+.[0-9]+.[0-9]+|[\+0-9]+\s[0-9]+\s[0-9]+\s[0-9]+\s[0-9]+|[\+0-9]+\s[0-9]+\s[0-9]+",phone_number)
    #print('content from phone_number',phone_regex) #beware, this is a list!
    #remove short matches such as '0 8008' from addresses that are found inside here
    phone_sane = [i for i in phone_regex if len(i) >7] #POSSIBLY missing some phone_numbers, check again
    tel = phone_sane[0].replace(" ","").replace('-','').replace('(0)','').replace(")",'').replace("(","")
    return tel

def scrape_likes(fb_url): 
    
    fb_likes = 0
    response = requests.get(fb_url)
    soup = BeautifulSoup(response.content,'lxml')
    #print('soup is',soup)
    f = soup.find('div', attrs={'class': '_4-u3 _5sqi _5sqk'})
    
    try:
        likes=f.find('span',attrs={'class':'_52id _50f5 _50f7'}) #finding span tag inside class
        #print(likes)
        x= re.findall("[0-9]+.[0-9]+.[0-9]+|[0-9]+",likes.text) #adapted regex to find numbers separated by 2 pts

        #change line to x[0].replace(',','') when using a non-german IP. only german site uses '.' as separator
        x[0]=x[0].replace('.','') 

        fb_likes = int(x[0])
        #if enough likes (arbitrary value here), get me also address
        #print('amount fb likes:',fb_likes
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

def scrape_site(url): #later take list of URLs as input 
    
    new_links = []
    site = url#input() #save page in variable to later print it with exception. -> change once automation begins
    cont = requests.get(site)

    soup = BeautifulSoup(cont.content,'lxml')
    links = [link.get('href') for link in soup.find_all('a')]
    #print('this is links:',links)

    #sites can be extended by '(at)' regex

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
    #print('email is currently of type:',type(email)) """
    
    if twitter:
        num_followers = get_twitter_followers(twitter[0])#num_followers is returned, put into df
        #print(twitter[0])
    else:
        twitter = [None]
        num_followers = None
        
    if facebook:
        fb_likes,tel,address = scrape_likes(facebook[0]) #returns fb_likes, tel, address
        #print(facebook[0]) #prints me fb link
    else:
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
    #put this declaration outside function if you want whole list later!    
    df = pd.DataFrame(columns=['fb_likes','twitter_followers','tel','url','fb_url','address','twitter_url','email','linkedin'])
    #print('fb likes:',fb_likes,'phone:',tel,'address:',address)
    
    try:
        #possibly add an if here as soon as you want to automate this part based on amount of likes etc.
        url = site.replace('https://','').replace('http://','') #better formatting for search in SF
        if(url.endswith('/')):
            url=url[:-1]
        stuff = [fb_likes,num_followers,tel,url,facebook[0],address,twitter[0],email,linkedinurl]
        #print('stuff prints:',stuff)
        
        #displays entire columns, change second parameter to char length. -1 is turned off.
        pd.set_option('display.max_colwidth', -1)
        
        df = df.append(pd.Series(stuff,index=df.columns),ignore_index=True)
        
        print(facebook[0])
        if linkedin:
            print(linkedin[0])
        show(df)
        
    except:
        #reduce amount of prints once this becomes automated based on list
        print('no stuff for',url)
       
        
        
    #return stuff        

scrape_site(input("Enter URL:"))