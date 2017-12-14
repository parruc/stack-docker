import logging
import os
import time

from selenium import webdriver

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create a new instance of the Firefox driver
browser = webdriver.Chrome()
URL = "http://www.ismeamercati.it/flex/cm/pages/ServeBLOB.php/L/IT/IDPagina/5390"
CSV_XPATH = "//a[text()='CSV (delimitato da virgole)']"
SUBMIT_XPATH = "//input[@value='Visualizza rapporto']"
SAVE_XPATH = "//a[@id='rptISMEAPREZZI_ctl06_ctl04_ctl00_ButtonLink']"
SRC_PATH = "/home/creepingdeath/Downloads/PO_Tab03.csv"
DEST_PATH = "/home/creepingdeath/Downloads/ismea"
SLEEPTIME = 5
GLOBAL_COUNTER = [0, 0, 0, 0, 0, 0]
OFFSET = [20, 0, 0, 0, 0, 0]


def switch_to_new_frame():
    browser.switch_to_default_content()
    frame = browser.find_element_by_tag_name('iframe')
    browser.switch_to_frame(frame)


def get_options(select_num):
    results = []
    selects = browser.find_elements_by_tag_name("select")
    select = selects[select_num]
    options = select.find_elements_by_tag_name("option")
    for option in options:
        if option.get_attribute('innerHTML') == "Tutti":
            return [option, ]
        if option.get_attribute("value") != "0":
            results.append(option)
    return results


def loop_select(file_parts):
    select_num = min(len(file_parts), 5)
    options = [o.get_attribute("value") for o in get_options(select_num)]
    for index, value in enumerate(options):
        counter_num = int(''.join(map(str, GLOBAL_COUNTER)))
        offset_num = int(''.join(map(str, OFFSET)))
        if offset_num > counter_num and OFFSET[select_num] > GLOBAL_COUNTER[select_num]:
            logger.info("Skipped" + str(GLOBAL_COUNTER))
            GLOBAL_COUNTER[select_num] += 1
            continue
        option = get_options(select_num)[index]
        try:
            file_parts[select_num] = option.get_attribute("innerHTML")
        except IndexError:
            file_parts.append(option.get_attribute("innerHTML"))
        logger.info(GLOBAL_COUNTER)
        logger.info(file_parts)
        option.click()
        time.sleep(SLEEPTIME)
        switch_to_new_frame()
        if select_num == 5:
            browser.find_element_by_xpath(SUBMIT_XPATH).click()
            time.sleep(SLEEPTIME)
            switch_to_new_frame()
            browser.find_element_by_xpath(SAVE_XPATH).click()
            time.sleep(1)
            switch_to_new_frame()
            browser.find_element_by_xpath(CSV_XPATH).click()
            time.sleep(SLEEPTIME)
            switch_to_new_frame()
            file_name = "_".join(file_parts).replace("&nbsp;", "-")
            file_name = file_name.replace("/", "-") + ".csv"
            while not os.path.exists(SRC_PATH):
                time.sleep(SLEEPTIME)
            time.sleep(1)
            if os.path.isfile(SRC_PATH):
                os.rename(SRC_PATH, os.path.join(DEST_PATH, file_name))
            else:
                raise ValueError("%s isn't a file!" % SRC_PATH)
        else:
            loop_select(file_parts.copy())
        GLOBAL_COUNTER[select_num] += 1
    GLOBAL_COUNTER[select_num] = 0


browser.get(URL)
time.sleep(2)
browser.find_element_by_id('eu-privacy-close').click()
switch_to_new_frame()
loop_select([])
