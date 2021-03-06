from selenium import webdriver
import tldextract
from datetime import datetime, timezone
import os
from PIL import Image
from types import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from urllib.parse import urlparse

screen_width=800
screen_height=1000
directory_base = "../server/test-images/"

# TODO: overwrite this with an environment variable that has the path in production
if os.environ.get('IMAGE_VOLUME'):
    directory_base = os.environ['IMAGE_VOLUME']


selenium_server_url = None

if os.environ.get('USE_DOCKER_HOST') and os.environ.get('DOCKER_HOST'):
    url = tldextract.extract(os.environ['DOCKER_HOST'])
    selenium_server_url = 'http://' + url.domain + ':4444' + '/wd/hub'
    print('found url: {}'.format(selenium_server_url))

# TODO: overwrite this with an environment variable that has the path in production
if os.environ.get('SELENIUM_HOST'):
    selenium_server_url = os.environ['SELENIUM_HOST']
    sleep(2) # give some time for the selenium server to start up

print("Directory base is {}".format(directory_base))
print("Selenium host is {}".format(selenium_server_url))

# This site is not responsive, we force their hand
normalize_javascript = """
      elem = document.querySelector('{}');
      if (elem) {{
          elem.style.color = "#000";
      }}
"""

adjust_background_color = """
      elem = document.querySelector('{}');
      // for good measure set both element and it's parent to white
      if (elem) {{
          elem.parentElement.style.backgroundColor="#fff";
          elem.style.backgroundColor = "#fff0";
      }}
"""

hide_element = """
      elem = document.querySelector('{}')
      if (elem) {{
          elem.style.display = "none"
      }}
"""

def webdriver_wait(driver, seconds):
    try:
        element = WebDriverWait(driver, seconds) \
        .until(EC.presence_of_element_located((By.ID, "this_is_a_fake_id")))
    except Exception:
        # this will always execute, we always ignore
        pass

def webdriver_scroll_into_view(driver, selector):
    # Although this seems to do nothing, it has a side effect of scrolling the
    # target element into view. Invoking javascript's Element.scrollIntoView,
    # though it works on the browser, seems to fail when run inside selenium.
    print("Scrolling {} into view".format(selector))
    content = driver.find_element_by_css_selector(selector)
    location = content.location_once_scrolled_into_view
    size = content.size


class Scraper():
    def __init__(self, url, selector):
        self.url = url
        self.selector = selector


    def get_options(self):
        options = webdriver.ChromeOptions()
        #options.set_headless(True)
        options.add_argument('--window-size={},{}'.format(screen_width, screen_height))
        return options


    def _init_driver(self):
        self.driver = webdriver.Chrome(chrome_options=self.get_options())
        self.driver.set_window_size(screen_width, screen_height)
        self.driver.scale = 2

    def _init_driver_remote(self):
        # Create a desired capabilities object as a starting point.
        capabilities = self.get_options().to_capabilities()

        # Instantiate an instance of Remote WebDriver with the desired capabilities.
        self.driver = webdriver.Remote(desired_capabilities=capabilities,
                                  command_executor=selenium_server_url)
        self.driver.scale = 1

    def get(self):
        zone = datetime.now(timezone.utc).astimezone().tzinfo
        time_slug = datetime.now(tz=zone).strftime("%Y-%m-%d-%H_%M%Z_")
        print("Fetching {} at {}".format(self.url, time_slug))

        if not hasattr(self, "driver"):
            if selenium_server_url:
                self._init_driver_remote()
            else:
                self._init_driver()

        self.driver.get(self.url)
        site_slug = directory_base + time_slug + tldextract.extract(self.url).domain
        original_filename =  site_slug + ".png"
        filename =  site_slug + "_working_copy" + ".png"

        if hasattr(self, "remove_ads"):
            self.remove_ads(self.driver)

        self.driver.save_screenshot(original_filename)
        bbox = self.find_bounding_box()
        self.driver.save_screenshot(filename)
        self.driver.quit()

        # still have to investigate what determines this scale
        scale = self.driver.scale
        x, y, w, h = bbox
        bbox = (x*scale, y*scale, w*scale, h*scale)

        with Image.open(filename) as im:
            cropped_filename = site_slug + "_cropped.png"
            cropped  = im.crop(bbox)
            cropped.save(cropped_filename, "PNG")
            print("saved " + cropped_filename)

        os.remove(filename)

    def find_bounding_box(self):
        if isinstance(self.selector, LambdaType):
            return self.selector(self.driver)

        content = self.driver.find_element_by_css_selector(self.selector)
        location = content.location_once_scrolled_into_view
        size = content.size

        self.driver.execute_script(adjust_background_color.format(self.selector))
        self.driver.execute_script(normalize_javascript.format(self.selector))
        x = location["x"]
        y = location["y"]
        w = size["width"]
        h = size["height"]
        return (x, y, x+w, y+h)


def remove_ads_nytimes(driver):
    try:
        if driver.find_element_by_css_selector("#signup-favor"):
            print("attempting to remove #signup-favor")
            driver.execute_script(hide_element.format("#signup-favor"))
    except:
        pass

    try:
        if driver.find_element_by_css_selector("#welc_supercontainer"):
            print("attempting to remove #welc_supercontainer")
            driver.execute_script(hide_element.format("#welc_supercontainer"))
    except:
        pass

nytimes_scraper = Scraper("https://nytimes.com", ".story-heading a")
nytimes_scraper.remove_ads = remove_ads_nytimes

def find_foxnews_bbox(driver):
    bg_selector = ".main-content .story-1 h2.title"
    link_selector = bg_selector + " a"
    content = driver.find_element_by_css_selector(bg_selector)
    location = content.location_once_scrolled_into_view
    size = content.size

    driver.execute_script(adjust_background_color.format(bg_selector))
    driver.execute_script(normalize_javascript.format(link_selector))

    x = location["x"]
    y = location["y"]
    w = size["width"]
    h = size["height"]
    return (x, y, x+w, y+h)
# scraper = Scraper("http://www.foxnews.com/", ".main-content h2.title")
foxnews_scraper = Scraper("http://www.foxnews.com/", find_foxnews_bbox)

def find_npr_bbox(driver):
    selector = ".story-text h1.title"
    content = driver.find_element_by_css_selector(selector)
    location = content.location_once_scrolled_into_view
    size = content.size
    slug = driver.find_element_by_css_selector('.story-text .slug')

    driver.execute_script(adjust_background_color.format(selector))
    driver.execute_script(normalize_javascript.format(selector))

    x = location["x"]
    y = location["y"]
    w = max(slug.size["width"], size["width"])
    h = size["height"]
    return (x, y, x+w, y+h)

npr_scraper = Scraper("https://www.npr.org/", find_npr_bbox)

washpost_scraper = Scraper("https://www.washingtonpost.com",
                           "#main-content .headline")

usatoday_selector = '.hfwmm-primary-hed p'
def remove_ads_usatoday(driver):
    click_button_javascript = """
      button = document.querySelector(\".partner-scroll-circle\");
      button != undefined && button.click();
      """
    driver.execute_script(click_button_javascript.format(usatoday_selector))

def find_usatoday_bbox(driver):
    selector = usatoday_selector
    content = driver.find_element_by_css_selector(selector)
    driver.execute_script(adjust_background_color.format(selector))
    driver.execute_script(normalize_javascript.format(selector))

    location = content.location_once_scrolled_into_view
    size = content.size

    x = location["x"]
    y = location["y"]
    w = size["width"]
    h = size["height"]
    return (x, y, x+w, y+h)

usatoday_scraper = Scraper("https://www.usatoday.com", find_usatoday_bbox)
usatoday_scraper.remove_ads = remove_ads_usatoday

if __name__ == '__main__':
    nytimes_scraper.get()
    foxnews_scraper.get()
    npr_scraper.get()
    washpost_scraper.get()
    usatoday_scraper.get()


