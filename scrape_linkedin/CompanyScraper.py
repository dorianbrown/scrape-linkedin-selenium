from .Scraper import Scraper
import json, re
from requests.utils import quote
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

import time
from .Company import Company
from .utils import AnyEC


class CompanyScraper(Scraper):
    def scrape(self, company_id=None, company_name=None, overview=True, jobs=False, life=False, insights=False):
        # Get Overview
        self.load_initial(company_id, company_name)

        jobs_html = life_html = insights_html = overview_html = ''

        if overview:
            overview_html = self.get_overview()
        if life:
            life_html = self.get_life()
        if jobs:
            jobs_html = self.get_jobs()
        return Company(overview_html, jobs_html, life_html)

    def load_initial(self, company_id, company_name):
        if company_name:
            company_id = self.get_company_id(company_name)
        url = 'https://www.linkedin.com/company/{}'.format(company_id)

        self.driver.get(url)
        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.organization-outlet')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")
        try:
            self.driver.find_element_by_css_selector('.organization-outlet')
        except:
            raise ValueError(
                'Company Unavailable: Company link does not match any companies on LinkedIn')

    def get_company_id(self, name):

        url = f"https://www.linkedin.com/search/results/companies/?keywords={quote(name)}"
        print(url)
        self.driver.get(url)

        try:
            myElem = WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.search-result__info')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
        except TimeoutException as e:
            raise ValueError(
                """Took too long to load company.  Common problems/solutions:
                1. Invalid LI_AT value: ensure that yours is correct (they
                   update frequently)
                2. Slow Internet: increase the timeout parameter in the Scraper constructor""")

        first_el = self.driver.find_element_by_css_selector(".company.search-result--occlusion-enabled")

        regex = r"href=\"\/company\/([\w-]+)"
        company_id = re.findall(regex, first_el.get_attribute("outerHTML"))
        if company_id:
            self.driver.get(f"https://www.linkedin.com/company/{company_id[0]}")
            WebDriverWait(self.driver, self.timeout).until(AnyEC(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.org-top-card')),
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, '.error-container'))
            ))
            return re.findall(r"([^\/]+)\/$", self.driver.current_url)[0]
        else:
            raise ValueError(f"Couldn't find company_id of '{name}'")

    def get_overview(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_about_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_about_tab"].active')
            return self.driver.find_element_by_css_selector(
                '.organization-outlet').get_attribute('outerHTML')
        except:
            return ''

    def get_life(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_life_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_life_tab"].active')
            return self.driver.find_element_by_css_selector('.org-life').get_attribute('outerHTML')
        except:
            return ''

    def get_jobs(self):
        try:
            tab_link = self.driver.find_element_by_css_selector(
                'a[data-control-name="page_member_main_nav_jobs_tab"]')
            tab_link.click()
            self.wait_for_el(
                'a[data-control-name="page_member_main_nav_jobs_tab"].active')
            return self.driver.find_element_by_css_selector('.org-jobs-container').get_attribute('outerHTML')
        except:
            return ''
