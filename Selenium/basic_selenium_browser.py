from selenium import webdriver

from webdriver_manager.chrome import ChromeDriverManager

def create_browser(headless=False):

    """
    Create an instance of Chrome browser through Selenium

    Args:
    headless (bool): Whether to operate windowless
    
    Returns:
    selenium webdriver.Chrome object"""

    options = webdriver.ChromeOptions()
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--incognito')

    if headless == True:
        # headless option for not opening window
        options.add_argument('--headless')

    return webdriver.Chrome(ChromeDriverManager().install(), options = options)

if __name__ == '__main__':

    site = 'www.google.com'

    test = create_browser()

    test.get(site)

    print(f'We opened {site} wep page!')