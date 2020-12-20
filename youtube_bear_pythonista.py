import re
import webbrowser
import requests
from bs4 import BeautifulSoup
import clipboard as p

### ASCII stuff for X-URL-Callback-String ###
space = "%20"
left_bracket_round = "%28"
right_bracket_round = "%29"
left_bracket_square = "%5B"
right_bracket_square = "%5D"
comma = "%2C"
colon = "%3A"
new_line = "%0A"
hashtag = "%23"
equal_sign = "%3D"
question_mark = "%3F"
slash = "%2F"
separator = "%20-%20"
horizontal_line = "---"
and_sign = "%26"
### ASCII stuff end ###
 
#different variations for opening note after completion or not
keep_note_closed = "&open_note=no&text="
open_note = "&open_note=yes&text="

begin = 'bear://x-callback-url/create?title='

link = p.get()

def conversion(sec):
   sec_value = sec % (24 * 3600)
   hour_value = sec_value // 3600
   sec_value %= 3600
   min_value = sec_value // 60
   sec_value %= 60

   return hour_value, min_value, sec_value

def create_seconds(time):

    m = re.match(r"PT(\d+)M(\d+)S", time)

    if m:
        minutes = int(m.group(1))
        seconds = int(m.group(2))
        return minutes*60 + seconds
    else:
        return None

def split_and_adjust_to_bear(string,bear=False):

    string = string.split()
    string = [i for i in string if i.isalpha()]

    if bear == True:
        return '%20'.join(string)

    else:
        return ' '.join(string)

def create_acronym(title):
    
    acronym = []
    title = split_and_adjust_to_bear(title)

    splitted_list = title.split()

    splitted_length = len(splitted_list)
    
    # border case that title does contain less than 4 words for acronym:
    if splitted_length < 1:
        raise ValueError('Length of title is too short')

    elif splitted_length == 1:
        acronym = splitted_list[0][:4].upper()

    elif splitted_length == 2 or splitted_length == 3:
        acronym = splitted_list[0][:2].upper() + splitted_list[1][:2].upper()
        #print('this is acronym: ',acronym)
        """i = 0
        while len(acronym) < 4:
            acronym.append(splitted_list[i][0].upper())
            print('this is acronym:', acronym)
            i += 1"""

    # if title consists of at least 4 separated words
    else:           

        for i in range(0,4):
            acronym.append(splitted_list[i][0].upper())

    return ''.join(acronym)+"%20-%20"

def make_soup(url):

    r = requests.get(url)

    soup = BeautifulSoup(r.content,features='html5lib')

    return soup

def get_yt_meta_content(url):

    soup = make_soup(url)

    ### this is how an example return from a beautifulsoup object looks like ###

    #<div class="watch-main-col"
    #  <meta content="Two Easily Remembered Questions That Silence Negative Thoughts | Anthony Metivier | TEDxDocklands" itemprop="name"/>

    title = soup.find("meta",  itemprop="name")['content']
    title_adjusted = split_and_adjust_to_bear(title,True)

    description = soup.find("meta",  itemprop="description")['content']
    description = split_and_adjust_to_bear(description,True)

    #change and reformat according to the one uniform format
    duration = create_seconds(soup.find("meta",  itemprop="duration")['content'])

    #likes = int(soup.find("meta",  itemprop="interactionCount")['content']) if interested, put likes in


    published_date = soup.find("meta",  itemprop="datePublished")['content']
    
    # adjusting url to Bear format is necessary as well
    url_adjusted = url.replace(':',colon).replace('/',slash).replace('?',question_mark).replace('=',equal_sign)


		# get the minutes and seconds separately again from note
    hourpart, minutepart, secondspart = conversion(duration)


    note_content = "%23videos%0A---%0AFlow%3A%5B%5BHelpful"+space+"Youtube"+space+"Videos%5D%5D%0A---%0A%5BYT%20Link%5D%28"+\
    url_adjusted+"%29%0A---%0APosted%20on%3A%"+published_date+"%20II%20Duration%20in%20minutes%3A%20"+str(hourpart)+colon+str(minutepart)+\
    colon+str(secondspart)+"%20("+str(duration)+"%20seconds)%0A---%0A"+"%23%23%20Description%0A"+description+"%0A---%0A%23%23%20Main%20Message"
    meta_info = [title_adjusted, duration, description, published_date, url, title]
    
    #return statement could potentially be dataframe in the future so that this row can then be appended to one big frame showing all videos.

    return (meta_info, note_content)

def create_book_title_note(link):

    #how do you get title and authors? beuatifulsoup?
    #####
    #####
    #####


    #acronym = str(input("Enter Acronym"))
    #title = str(input("Enter book <title>, optional format <Title>:<Subtitle>")).replace(":",colon).replace(" ",space)
    title = c.split_and_adjust_to_bear(title)
    #authors = str(input("Enter authors comma separated")).replace(",",comma).replace(" ",space)
    authors = c.split_and_adjust_to_bear(authors)
    #year = str(input("Enter release year"))
    #toc = []
    #amount_chapters = int(input("Enter amount of chapters you want to create"))
    amount_chapters = len(toc)
    #for j in range(0,amount_chapters):
        #toc.append(input("chapter name "+str(j)+" here"))
    
    title = (acronym+c.separator+authors+
    c.space+c.left_bracket_round+year+
    c.right_bracket_round+c.separator+title)


    #general book note content
    note_content = "%23books%20%23discussions%0A---%0AFlow%3A%5B%5BBooks%5D%5D%26%26%5B%5BDiscussions"+\
    "%5D%5D%0A---%0A%5BGoodreads%20Link%5D%28www.goodreads.com%29%0A---%0A%23%23%20"+\
    "Synopsis%0A---%0A%23%23%20Chapters"
    


    toc_xcallback = [i.replace(" ",c.space).replace(",",c.comma).replace(":",c.colon) for i in toc]
    
    flexible_chapter_content = ""
    for i in range(0,amount_chapters):
        flexible_chapter_content += "%0A%5B%5B"+acronym+"%20-%20"+str(i+1)+"%2F"+str(amount_chapters)+"%3A"+toc_xcallback[i]+"%5D%5D%0A%3E%20Quote"
                                        
    content = note_content+flexible_chapter_content

    return title, content


def create_note(link):

    ### case youtube ###

    if "youtu" in link:
        metainfo, content = get_yt_meta_content(link)
        title = metainfo[0]
        print('metainfo is:',metainfo)
        acronym = create_acronym(metainfo[-1])

    ### case goodreads ###

    elif "goodreads" in link:
        #title, content = b.create_book_title_note(link)
        print("elif")

    else:
        print("None of the cases was caugth from:",link)

    final = begin+acronym+title+open_note+content
    print('this is final:',final)
    
    return final


webbrowser.open(create_note(link))