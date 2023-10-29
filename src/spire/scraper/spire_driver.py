# type: ignore

import logging
from enum import Enum
from time import sleep
from typing import Union

from django.conf import settings
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import Firefox, Remote
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait

log = logging.getLogger(__name__)


class SpirePage(Enum):
    CourseCatalog = "Browse Course Catalog"
    ClassSearch = "Search for Classes"


class SpireDriver:
    def __init__(self):
        log.info("Creating driver...")

        selenium_server_url = settings.SCRAPER["SELENIUM_SERVER_URL"]
        if selenium_server_url:
            self._driver = Remote(
                command_executor=selenium_server_url, options=Options()
            )
        else:
            self._driver = Firefox(options=Options())

        self._wait = WebDriverWait(self._driver, 60 * 2)

        self._state = "none"

        retry_count = 0
        while self._state != "default":
            try:
                self._start()
            except Exception as e:
                if retry_count >= 3:
                    raise e

                log.exception("Failed to start driver: %s", e)

                retry_count += 1
                sleep(60)

        log.info("Driver created.")

    def _start(self):
        self._driver.get("https://www.spire.umass.edu")

        self._wait.until(
            EC.element_to_be_clickable((By.NAME, "CourseCatalogLink"))
        ).click()

        self._wait.until(EC.title_is("Search for Classes"))

        self.wait_for_spire()

        self._state = "default"

    @property
    def root_driver(self) -> Firefox:
        return self._driver

    def switch(self):
        log.debug("Switching focus...")
        if self._state == "default":
            self._wait.until(
                EC.frame_to_be_available_and_switch_to_it((By.NAME, "TargetContent"))
            )
            self._state = "iframe"
        elif self._state == "iframe":
            self._driver.switch_to.default_content()
            self._state = "default"

        log.debug("Switched focus to: %s", self._state)

    # def navigate_to(self, page: SpirePage) -> None:
    #     log.info("Navigating to %s...", page)
    #
    #     if self._state != "default":
    #         self.switch()
    #
    #     self.click("pthdr2search")
    #
    #     search_input: WebElement = self.wait_for_interaction(By.ID, "pthdr2srchedit")
    #     search_input.clear()
    #     search_input.send_keys(page.value.lower())
    #
    #     self.click("pthdrSrchHref")
    #
    #     self.switch()
    #
    #     self.click("#ICSetFieldPTSF_GLOBAL_SEARCH.TREECTLEVENT.S3")
    #     self.click("srchRsltUrl$0")
    #
    #     self._wait.until(EC.title_is(page.value))
    #
    #     log.info("Navigated to %s.", page)

    def click(self, selector: str, by: str = By.ID, wait: bool = True):
        element = self._wait.until(EC.element_to_be_clickable((by, selector)))

        self.scroll_to(element)
        ActionChains(self._driver).move_to_element(element).click().perform()
        log.debug("Clicked element %s: %s", by, selector)

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
        self._wait.until_not(
            EC.text_to_be_present_in_element_attribute(
                (By.CSS_SELECTOR, "body.PSPAGE"), "style", "none"
            )
        )

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
        log.info("Closing driver...")
        self._driver.close()
