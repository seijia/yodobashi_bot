# coding: utf-8

from selenium import webdriver
from selenium_stealth import stealth
import time
import os
import copy
import logging
import config
import xpath as xp
from datetime import datetime
from selenium.webdriver.support.ui import WebDriverWait

log_fmt = '%(levelname)s %(asctime)s: %(message)s'
date_fmt = '%Y-%m-%d %H:%M:%S'
log_file_name = "{}/log/yodobashi-{}.log".format(
    os.getcwd(), datetime.now().strftime("%Y-%m-%d"))
handlers = [logging.FileHandler(log_file_name, encoding='utf-8'), logging.StreamHandler()]
logging.basicConfig(level=logging.INFO,
                    format=log_fmt,
                    datefmt=date_fmt,
                    handlers=handlers)

logger = logging.getLogger(__name__)

wait_time = config.wait_time

check_local_store = config.check_local_store


def auto_login(driver):
    WebDriverWait(driver, wait_time).until(
        lambda d: d.find_element_by_xpath(xp.login_text))
    driver.find_element_by_xpath(xp.member_id_input).send_keys(
        config.login_info["user"])
    driver.find_element_by_xpath(
        xp.password_input).send_keys(config.login_info["ps"])
    driver.find_element_by_xpath(xp.login_button).click()


def add_to_cart(driver, buy_list):
    # prepare to buy
    for t, product_link in buy_list:
        driver.get(product_link)
        WebDriverWait(driver, wait_time).until(
            lambda d: d.find_element_by_xpath(xp.add_to_shopping_cart_button))
        driver.find_element_by_xpath(xp.add_to_shopping_cart_button).click()
    driver.find_element_by_xpath(xp.proceed_to_shoppingcart_button).click()
    WebDriverWait(driver, wait_time).until(
        lambda d: d.find_element_by_xpath(xp.shoppingcart_text))
    driver.find_element_by_xpath(xp.proceed_to_next_button).click()
    try:
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element_by_xpath(xp.confirm_button))
    except:
        auto_login(driver)
        WebDriverWait(driver, 10).until(
            lambda d: d.find_element_by_xpath(xp.proceed_to_next_button))

    driver.find_element_by_xpath(xp.sec_input).send_keys(config.key)
    driver.find_element_by_xpath(xp.confirm_button).click()
    return True


def check_web(driver, t):
    # check stock arrival
    driver.get(xp.base_url + t)
    elms = driver.find_elements_by_xpath(xp.store_list)
    stock_list = []
    for elem in elms:
        status = elem.find_elements_by_xpath(xp.product_status)
        text = [s.text for s in status]
        text = " ".join(text)
        flags = [t in text for t in xp.over_text]
        if True not in flags:
            xp.sed_notice(text, xp.base_url+t, t)
            product_link = elem.find_element_by_xpath(
                xp.page_link).get_attribute('href')
            stock_list.append((t, product_link))
        try:
            if check_local_store:
                check_local_store_stock(driver, elem)
        except:
            pass
    return stock_list


def check_local_store_stock(driver, elem):
    # check if local store Arrivaled
    store = elem.find_element_by_xpath(xp.store_number_xpath)
    if store.text and store.text != xp.no_store_text:
        store.find_element_by_xpath("./a").click()
        time.sleep(3)
        check_store_list_name(driver)


def check_store_list_name(driver):
    # check local store page
    driver.switch_to.window(driver.window_handles[1])
    driver.find_element_by_xpath(xp.ishii_sport_checkbox).click()
    driver.find_element_by_xpath(xp.art_sport_checkbox).click()
    driver.find_element_by_xpath(xp.filter_store_checkbox).click()

    store_list = driver.find_elements_by_xpath(xp.stock_store_list)
    for store in store_list:
        name = store.find_element_by_xpath(xp.store_name).text
        status = store.find_element_by_xpath(xp.store_status).text
        logger.info(name + ":" + status)

    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    return


def main(driver, targets):
    target = copy.copy(targets)
    buy_list = []
    for t in target:
        stock = check_web(driver, t)
        buy_list = buy_list + stock
    return buy_list


def read_targets():
    targets = None
    with open(config.target_file, 'r', encoding='UTF-8') as f:
        targets = f.readlines()

    targets = [t for t in targets if t[0] != "#" and t != "\n"]
    targets = [t.replace(" ", "+") for t in targets if t != "\n"]
    return targets


if __name__ == "__main__":
    driver = xp.start_chrome()
    exit_flag = False
    targets = read_targets()
    while not exit_flag and targets:

        hour_now = datetime.now().hour
        min_now = datetime.now().minute
        # sleep in 23.pm to 9.am
        if hour_now < 9 or hour_now > 23:
            time.sleep(600)

        buy_list = main(driver, targets)
        if buy_list:
            u_driver = xp.start_undetected_chrome()
            add_to_cart(u_driver, buy_list)
        # remove product after was buy
        for t, _ in buy_list:
            targets.remove(t)

        time.sleep(20)

    else:
        logger.info("target is empty, exit")
        os.exit(0)
