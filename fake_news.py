from selenium import webdriver
from slugify import slugify
import time
from PIL import Image

class Scraper():
    def __init__(self, url, element_finder):
        options = webdriver.ChromeOptions()
        # options.add_argument("headless")
        options.add_argument('--window-size=500x800')
        self.driver = webdriver.Chrome(chrome_options=options)
        self.driver.set_window_size(500, 800)
        self.url = url
        self.element_finder = element_finder

    def get(self):
        self.driver.get(self.url)
        time.sleep(2) # wait for ads to go away
        content = self.element_finder(self.driver)
        filename = slugify(self.url) + ".png"
        self.driver.save_screenshot(filename)
        location = content.location_once_scrolled_into_view
        size = content.size
        self.driver.quit()

        # still have to investigate what determines this scale
        scale = 2
        x = location["x"] * scale
        y = location["y"] * scale
        w = size["width"] * scale
        h = size["height"] * scale

        bbox = (x, y, x+w, y+h)
        print(bbox)
        with Image.open(filename) as im:
            cropped_filename = slugify(self.url) + "_cropped.png"
            cropped  = im.crop(bbox)
            cropped.save(cropped_filename, "PNG")
            print("saved " + cropped_filename)

# scraper = Scraper("https://nytimes.com",
#                   lambda d: d.find_element_by_css_selector('.story-heading a'))
# scraper.get()

scraper = Scraper("http://www.foxnews.com/",
                  lambda d: d.find_element_by_css_selector('article.story-1 h2.title'))
scraper.get()
# print(dir(content))


