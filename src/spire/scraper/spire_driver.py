# type: ignore

import logging
from typing import Union

from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

log = logging.getLogger(__name__)


class SpireDriver:
    def __init__(self):
        options = Options()
        options.headless = settings.SCRAPER_HEADLESS
        self._driver = WebDriver(options=options)

        self._wait = WebDriverWait(self._driver, 60 * 2)

        self._driver.get("https://www.spire.umass.edu")

        self._wait.until(EC.element_to_be_clickable((By.NAME, "CourseCatalogLink"))).click()

        self._state = "default"

    @property
    def root_driver(self) -> WebDriver:
        return self._driver

    def switch(self):
        log.debug("Switching focus...")
        if self._state == "default":
            self._wait.until(EC.frame_to_be_available_and_switch_to_it((By.NAME, "TargetContent")))
            self._state = "iframe"
        elif self._state == "iframe":
            self._driver.switch_to.default_content()
            self._state = "default"

        log.debug("Switched focus to: %s", self._state)

    # ! New spire has no navigation
    # def navigate_to(self, page: str) -> None:
    #     assert page in ("catalog", "search")
    #     log.debug("Navigating to %s...", page)

    #     if self._state != "default":
    #         self.switch()

    #     self.click("pthnavbca_UM_COURSE_GUIDES", wait=False)
    #     self.click(
    #         "crefli_HC_SSS_BROWSE_CATLG_GBL4" if page == "catalog" else "crefli_HC_CLASS_SEARCH_GBL",
    #         wait=False,
    #     )
    #     self.switch()

    #     self.wait_for_spire()

    #     assert ("Browse Course Catalog" if page == "catalog" else "Search for Classes") == self._driver.title

    #     log.debug("Navigated to %s.", page)

    def click(self, selector: str, by: str = By.ID, wait: bool = True):
        element = self._wait.until(EC.element_to_be_clickable((by, selector)))

        self.scroll_to(element)
        ActionChains(self._driver).move_to_element(element).click().perform()

        if wait:
            self.wait_for_spire()

    def scroll_to(self, element: WebElement):
        coords = element.location
        self._driver.execute_script(f"window.scrollTo({coords['x']},{coords['y']});")

    def wait_for_presence(self, by: str, selector: str):
        log.debug("Waiting for presence of element by locator %s:%s...", by, selector)
        return self._wait.until(EC.visibility_of_element_located((by, selector)))

    def wait_for_interaction(self, by: str, selector: str):
        log.debug("Waiting for clickable element by locator %s:%s...", by, selector)
        return self._wait.until(EC.element_to_be_clickable((by, selector)))

    def wait_for_spire(self) -> None:
        log.debug("Waiting for spire...")
        self._wait.until_not(EC.visibility_of_element_located((By.ID, "processing")))

    def find(self, id: str, by: str = By.ID) -> Union[WebElement, None]:
        try:
            return self._driver.find_element(by, id)
        except NoSuchElementException:
            return None

    def find_all(self, selector: str, by: str = By.CSS_SELECTOR) -> list[WebElement]:
        return self._driver.find_elements(by, selector)

    def find_all_ids(self, selector: str, by: str = By.CSS_SELECTOR) -> list[str]:
        return [e.get_property("id") for e in self.find_all(selector, by)]

    def close(self) -> None:
        self._driver.close()
