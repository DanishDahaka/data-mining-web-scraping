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
### ASCII stuff end, potentially, this can be called from another file ###

#different variations for opening note after completion or not
keep_note_closed = "&open_note=no&text="
open_note = "&open_note=yes&text="

begin = 'bear://x-callback-url/create?title='

link = p.paste()

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

    #print('this is description:',description)

    published_date = soup.find("meta",  itemprop="datePublished")['content']

    # adjusting url to Bear format is necessary as well
    url_adjusted = url.replace(':',colon).replace('/',slash).replace('?',question_mark).replace('=',equal_sign)

    # get the minutes and seconds separately again from note
    hourpart, minutepart, secondspart = conversion(duration)

    note_content = "%23videos%0A---%0AFlow%3A%5B%5BHelpful"+space+"Youtube"+space+"Videos%5D%5D%0A---%0A%5BYT%20Link%5D%28"+\
    url_adjusted+"%29%0A---%0APosted%20on%3A%"+published_date+"%20II%20Duration%20in%20minutes%3A%20"+str(hourpart)+colon+str(minutepart)+\
    colon+str(secondspart)+"%20("+str(duration)+"%20seconds)%0A---%0A"+"%23%23%20Description%0A"+description+"%0A---%0A%23%23%20Main%20Message"

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
    #print(title)

    splitted_list = title.split()

    #print('splitted_list:',splitted_list)

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
    soup = BeautifulSoup(r.content,"html.parser")
    return soup


def create_note(link):

    ### case youtube ###

    if "youtu" in link:
        metainfo, content = get_yt_meta_content(link)
        title = metainfo[0]
        acronym = create_acronym(metainfo[-1])
        #print(metainfo)
        final = begin+acronym+title+open_note+content
        #print(final)

    else:
        print("None of the cases was caugth from:",link)
        final = None
    
    return final

# testing with Data Science video from YouTube
print(create_note('https://www.youtube.com/watch?v=zMfP-6a7fTo'))


# uncomment to open a bear note with a URL from the clipboard
#webbrowser.open(create_note(link))
