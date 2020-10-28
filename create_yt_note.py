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

link = p.paste()

def create_seconds(time):

    m = re.match(r"PT(\d+)M(\d+)S", time)

    if m:
        minutes = int(m.group(1))
        seconds = int(m.group(2))
        return minutes*60 + seconds
    else:
        return None

def get_yt_meta_content(url):

    soup = make_soup(url)

    ### this is how an example return from a beautifulsoup object looks like ###

    #<div class="watch-main-col"
    #  <meta content="Two Easily Remembered Questions That Silence Negative Thoughts | Anthony Metivier | TEDxDocklands" itemprop="name"/>

    title = soup.find("meta",  itemprop="name")['content']
    title_adjusted = split_and_adjust_to_bear(title,True)

    description = soup.find("meta",  itemprop="description")['content']
    description = split_and_adjust_to_bear(description,True)

    duration = create_seconds(soup.find("meta",  itemprop="duration")['content'])

    published_date = soup.find("meta",  itemprop="datePublished")['content']


    note_content = "%23videos%0A---%0AFlow%3A%5B%5BHelpful"+space+"Youtube"+space+"Videos%5D%5D%0A---%0A%5BYT%20Link%5D%28"+\
    url+"%29%0A---%0A%23%23%20Description%0A"+description+"%0A---%0A%23%23%20Main%20Message"

    meta_info = [title_adjusted, duration, description, published_date, url, title]

    return (meta_info, note_content)

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

    for i in range(0,4):
        acronym.append(splitted_list[i][0].upper())

    return ''.join(acronym)+"%20-%20"

def make_soup(url):

    r = requests.get(url)
    soup = BeautifulSoup(r.content,"html.parser")
    return soup


def create_note(link):

    ### case youtube ###

    if "youtu" in link:
        metainfo, content = get_yt_meta_content(link)
        title = metainfo[0]
        acronym = create_acronym(metainfo[-1])
        final = begin+acronym+title+open_note+content

    else:
        print("None of the cases was caugth from:",link)
        final = None
    
    return final

webbrowser.open(create_note(link))
