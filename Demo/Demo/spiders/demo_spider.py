import scrapy
from scrapy.linkextractors import LinkExtractor
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.selector import Selector

from Demo.items import DemoItem

class DemoSpider(scrapy.Spider):
    name = "demo"

    allowed_domains = ['https://www.ibm.com']

    start_urls = ['https://www.ibm.com/support/knowledgecenter/SSEPGG_9.7.0/com.ibm.db2.luw.kc.doc/welcome.html']

    def __init__(self):
        scrapy.Spider.__init__(self)
        # using a firefox driver, for production use we can use a PhantomJS browser.
        self.driver = webdriver.Firefox()

    def __del__(self):
        try:
            scrapy.Spider.__del__(self)
        except AttributeError:
            # Method does not exist.  What now?
            print "no __del__ method exists in parent"

    def parse(self, response):
        self.logger.info("This url has been identified - " + response.url)
        sel = Selector(response)
        self.driver.get(response.url)
        #wait for the iframe to load, beacuse the iframes are loaded via AJAX, after the initial page load
        try:
            frame = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "iframe"))
            )
            self.logger.info(frame)
        except Exception:
            #quitting driver of no iframe was found
            self.logger.info('quitting driver')
            self.driver.quit()

        # Switching the search to the iframe on the page.
        self.driver.switch_to.frame(frame)

        #We are looking for links containing text 'driver', can be changed too look for multiples keywords & conditions
        xpath="//a[contains(text(), 'driver')]"
        links = self.driver.find_elements_by_xpath(xpath)
        # collect data from links
        for a in links:
            item = DemoItem()
            item['title'] = a.text
            item['link'] = a.get_attribute('href')
            yield item

        # follow the links and repeat parsing
        for link in links:
            url = link.get_attribute('href')
            proper_url = response.urljoin(url)
            self.logger.info("next url to be crawled - %s" % proper_url)

            # here 'dont_filter' is necessacry because scrapy will filter any request initiated by the user.
            yield scrapy.Request(url=proper_url, callback=self.parse, dont_filter=True)
