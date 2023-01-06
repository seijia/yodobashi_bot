import logging

from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium import webdriver
import undetected_chromedriver.v2 as uc

from webdriver_manager.chrome import ChromeDriverManager
from plyer import notification
import pickle
import winsound


home_page = "https://www.yodobashi.com/"
over_text = ['販売を終了しました', "販売休止中です", "予約受付を終了しました", "ただいま予約販売準備中！"]
no_store_text = "在庫のある店舗（0）"

# search page
base_url = "https://www.yodobashi.com/category/141001/141336/146471/?word="
store_list = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='contentsCol clearfix']/div[@class='mainCol']/div[@class='mainColInner']/div[@id='listContents']/div[@class='srcResultItem spt_hznList tileTypeList js_productList changeTile']/div[@class='srcResultItem_block pListBlock hznBox js_productBox js_smpClickable js_latestSalesOrderProduct productListTile']"
stock_status = "./div[@class='pInfo']/ul[@class='js_addLatestSalesOrder']/li"
page_link = "./a[@class='js_productListPostTag js-clicklog js-clicklog_OPT_CALLBACK_POST js-taglog-schRlt js_smpClickableFor cImg js-clicklog-check']"
store_number = "div[@class='storeStockLink spNone mt05']"

# local store page
ishii_sport_checkbox = "html/body/div[@id='wrapper']/div[@id='contents']/div[@class='contentsHeader sticky2']/div[@class='contentsHeadSub']/div[@class='headFilter']/div[@class='navInner']/span[@id='storeBrandFilter']/span/ul[@id='js_storeTypeSelect']/li[2]/div[@class='storeIcon store storeLink']/label[@class='storeCheckbox']/span[@class='store']"
art_sport_checkbox = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='contentsHeader sticky2']/div[@class='contentsHeadSub']/div[@class='headFilter']/div[@class='navInner']/span[@id='storeBrandFilter']/span/ul[@id='js_storeTypeSelect']/li[3]/div[@class='storeIcon store storeLink']/label[@class='storeCheckbox']/span[@class='store']"
filter_store_checkbox = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='contentsHeader sticky2']/div[@class='contentsHeadSub']/div[@class='headFilter']/div[@class='navInner']/span[@class='filterArea'][2]/span/ul[@id='js_stockSelect']/li/label/span[@class='filterItem']"
stock_store_list = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='colBase']/div[@class='colMain']/div[@class='container']/div[@class='storeInfoListBase']/div[@class='storeInfoList']/div[@class='ctgrNavBody']/div[@class='ctgrNavList navInner']/ul/li[@class='prefAccodionTabl']/div[@class='scndCate']/div[@id='js_storeList']/div[@class='entryBlock js_entryBlock']"
store_name = "./div[@class='shopInfoUnit']/table/tbody/tr[@class='rowData rowDataFirst']/td[@class='infoArea']/table/tbody/tr/td/div/div[@class='storeInfoCell mu5']/div[@class='storeInfoCellLeft']/div[@class='storeName']/div[@class='storeNameText']/a"

# login page
login_text = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/div[@class='mainCol']/form[@id='js_i_form']/div[@class='contentsHead']/div[@class='contentsTtl']"
member_id_input = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/div[@class='mainCol']/form[@id='js_i_form']/div[@class='ecContainer'][1]/div[@class='loginEntry ecOrderContainerFrame pa10']/div[@class='entryBlock']/div[@class='entrySelector js_c_loginTypeArea active']/div[@class='loginSelectUnit slctInputUnit']/table/tbody/tr/td[@class='loginInputArea']/div[@class='loginInner']/ul[@class='liMt05Fn']/li[1]/div[@class='inputUnit']/table/tbody/tr/td/input[@id='memberId']"
password_input = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/div[@class='mainCol']/form[@id='js_i_form']/div[@class='ecContainer'][1]/div[@class='loginEntry ecOrderContainerFrame pa10']/div[@class='entryBlock']/div[@class='entrySelector js_c_loginTypeArea active']/div[@class='loginSelectUnit slctInputUnit']/table/tbody/tr/td[@class='loginInputArea']/div[@class='loginInner']/ul[@class='liMt05Fn']/li[2]/div[@class='inputUnit']/table/tbody/tr/td/input[@id='password']"
login_button = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/div[@class='mainCol']/form[@id='js_i_form']/div[@class='ecContainer'][2]/div[@class='sbmBlock']/div[@class='hznList']/ul[@class='alignC']/li/div[@class='strcBtn30']/a[@id='js_i_login0']/span/strong"


# product detail page
add_to_shopping_cart_button = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@id='productDetail']/form/div[@class='pdTopContainer']/div[@class='pDetailBuyCol']/div[@id='js_buyBox']/div[@id='js_buyBoxMain']/ul[@class='buyBtn']/li[@class='yBtnStack yBtn yBtnPrimary yBtnMedium']/a[@id='js_m_submitRelated']"
product_status = "./div[@class='pInfo']/ul[@class='js_addLatestSalesOrder']/li"

# shoppingcart/recommend
proceed_to_shoppingcart_button = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='mainCol']/div[@class='ecContainer']/div[@class='feedbackTop clearfix']/div[@class='side']/div[@class='cartinBox']/div[@class='buyButton']/ul[@class='hznList']/li[@class='ml05']/div[@class='strcBtn30']/a[@class='btnRed']/span"


# shoppingcart
shoppingcart_text = "/html/body/div[@id='wrapper']/div[@id='contents']/form[@id='js_i_cart']/div[@id='js_flexFixedContentsBase']/div[@class='mainCol']/div[@class='contentsHead']/h1"
proceed_to_next_button = "/html/body/div[@id='wrapper']/div[@id='contents']/form[@id='js_i_cart']/div[@id='js_flexFixedContentsBase']/div[@class='rightCol']/div[@class='scrollFixedBox js_flexFixedContents']/div[@class='ecContainer']/div[@class='summaryBox']/div[@class='summaryBoxTop']/div[@class='checkout']/div[@class='yBtnStack']/span[@class='yBtn yBtnPrimary yBtnMedium']/span[@class='yBtnInner']/a[@id='sc_i_buy']/span"

# order confirm
sec_input = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/form[@id='js_i_form']/div[@class='ecContainer'][1]/div[@class='orderEntryTop ecOrderContainerFrame']/table/tbody/tr/td[@class='orderEntryTopColL']/div[@class='dashboard']/table/tbody/tr[1]/td[3]/div[@class='dashboardElement']/div[@class='body']/div[@class='fs11']/ul/li[@id='js_c_securityCodeAreaView']/div[@class='dashbordInputUnit']/table/tbody/tr/td/input[@class='uiInput fs11 js_c_securityCode ']"
confirm_button = "/html/body/div[@id='wrapper']/div[@id='frame']/div[@id='contents']/form[@id='js_i_form']/div[@class='ecContainer'][1]/div[@class='orderEntryTop ecOrderContainerFrame']/table/tbody/tr/td[@class='orderEntryTopColR']/div[@class='summary']/div[@class='buyButton']/div[@class='strcBtn36 alignC js_c_orderButton']/a[@class='btnRed js_c_order js_c_filterBtn']/span[@class='fs18']/strong"

# homepage
to_login_page = "/html/body/div[@id='wrapper']/div[@id='header']/div[@id='headerTop']/div[@class='nameDataArea']/p[@id='logininfo']/a[@class='clicklog cl-hdLO2_1']"
logo = "/html/body/div[@id='wrapper']/div[@id='header']/div[@id='headerTop']/h1[@id='headerLogo']/a[@id='headerLogoC']/img/@src"
product_name_xpath = "./a[@class='js_productListPostTag js-clicklog js-clicklog_OPT_CALLBACK_POST js-taglog-schRlt js_smpClickableFor cImg js-clicklog-check']/div[@class='pName fs14']/p[2]"
title = "/html/body/div[@id='wrapper']/div[@id='contents']/div[@class='contentsCol clearfix']/div[@class='mainCol']/div[@class='mainColInner']/div[@class='contentsHead js_legoPartsHeadline externalInputHeadline']/h1"
store_status_xpath = "./div[@class='shopInfoUnit']/table/tbody/tr[@class='rowData rowDataFirst']/td[@class='stockArea']/span[@class='uiIconTxtS']/span[@class='green']"

logger = logging.getLogger(__name__)


def start_chrome():
    options = Options()
    options.binary_location = 'C:\Program Files (x86)\Google\Chrome\Application\chrome.exe'
    options.add_argument(
        f'user-agent=Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US) AppleWebKit/525.19 (KHTML, like Gecko) Chrome/79.0.3945.79 Safari/537.36')

    # 以下のように使用するChromeDriverのヴァージョン指定ができる
    driver_version = '108.0.5359.71'
    chrome_service = ChromeService(
        ChromeDriverManager(version=driver_version).install())

    driver = webdriver.Chrome(service=chrome_service, options=options)

    driver.get('https://google.com')

    driver.implicitly_wait(30)
    return driver


def start_undetected_chrome():
    driver = uc.Chrome(use_subprocess=True)

    driver.get('https://www.yodobashi.com')
    load_cookie(driver, "./cookie")
    driver.implicitly_wait(10)

    return driver


def close_webdriver(driver):
    driver.quit()


def save_cookie(driver, path):
    with open(path, 'wb') as filehandler:
        pickle.dump(driver.get_cookies(), filehandler)


def load_cookie(driver, path):
    with open(path, 'rb') as cookiesfile:
        cookies = pickle.load(cookiesfile)
        for cookie in cookies:
            driver.add_cookie(cookie)

# send windows popup notification


def sed_notice(text, url, title):
    logger.warning(title + " " + text)
    logger.warning(url)

    notification.notify(
        title=title,
        message=url,
        app_name="ヨドバシチェック"
    )
    winsound.PlaySound("SystemHand", winsound.SND_ALIAS)
