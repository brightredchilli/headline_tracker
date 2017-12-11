from selenium import webdriver
from slugify import slugify
import time
import tldextract
from datetime import datetime
from PIL import Image
from types import *
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os

directory_base = "images/"

# This site is not responsive, we force their hand
normalize_javascript = """
      elem = document.querySelector('{}');
      elem.style.color = "#000";
      elem.style.width = \"400px\";
"""

adjust_background_color = """
      elem = document.querySelector('{}');
      // for good measure set both element and it's parent to white
      elem.parentElement.style.backgroundColor="#fff";
      elem.style.backgroundColor = "#fff";
"""


def webdriver_wait(driver, seconds):
    try:
        element = WebDriverWait(driver, seconds) \
        .until(EC.presence_of_element_located((By.ID, "this_is_a_fake_id")))
    except Exception:
        # this will always execute, we always ignore
        pass

class Scraper():
    def __init__(self, url, selector):
        self.url = url
        self.selector = selector

    def _init_driver(self):
        options = webdriver.ChromeOptions()
        options.add_argument("headless")
        options.add_argument('--window-size=500x800')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_window_size(800, 800)

    def get(self):
        time_slug = datetime.now().strftime("%Y-%m-%d-%H_%M")
        print("Feching {} at {}".format(self.url, time_slug))

        if not hasattr(self, "driver"):
            self._init_driver()

        self.driver.get(self.url)
        webdriver_wait(self.driver, 2) # wait for ads to disappear
        site_slug = directory_base + time_slug + "_" + tldextract.extract(self.url).domain
        original_filename =  site_slug + ".png"
        filename =  site_slug + "_working_copy" + ".png"

        if hasattr(self, "remove_ads"):
            self.remove_ads(self.driver)

        self.driver.save_screenshot(original_filename)
        bbox = self.find_bounding_box()
        webdriver_wait(self.driver, 1)
        self.driver.save_screenshot(filename)
        self.driver.quit()

        # still have to investigate what determines this scale
        scale = 2
        x, y, w, h = bbox
        bbox = (x*scale, y*scale, w*scale, h*scale)
        print(bbox)

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


nytimes_scraper = Scraper("https://nytimes.com", ".story-heading a")

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
                           "#main-content .headline a")

def remove_ads_usatoday(driver):
    click_button_javascript = """
      button = document.querySelector(\".partner-scroll-circle\");
      button != undefined && button.click();
      """
    driver.execute_script(click_button_javascript)
    webdriver_wait(driver, 1)

def find_usatoday_bbox(driver):
    selector = '.hfwmm-primary-hed p'
    content = driver.find_element_by_css_selector(selector)
    driver.execute_script(adjust_background_color.format(selector))
    driver.execute_script(normalize_javascript.format(selector))

    webdriver_wait(driver, 2)

    location = content.location_once_scrolled_into_view
    size = content.size

    x = location["x"]
    y = location["y"]
    w = size["width"]
    h = size["height"]
    return (x, y, x+w, y+h)

usatoday_scraper = Scraper("https://www.usatoday.com", find_usatoday_bbox)
usatoday_scraper.remove_ads = remove_ads_usatoday

nytimes_scraper.get()
foxnews_scraper.get()
npr_scraper.get()
washpost_scraper.get()
usatoday_scraper.get()

# print(dir(content))


