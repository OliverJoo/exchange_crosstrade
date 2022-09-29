import os
import pathlib
# 실행하는 파일의 경로로 현재 작업 디렉토리를 변경 for ubuntu
os.chdir(pathlib.Path(__file__).parent.absolute())

import itertools

import pandas as pd
from tabulate import tabulate
from pretty_html_table import build_table

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import urllib.error as urle
import datetime
# for local test
from selenium.webdriver.chrome.options import Options

# custom utils
from oliver_util_package import crawling_utils
from oliver_util_package import log_utils
from oliver_util_package import email_utils

logger = log_utils.logging.getLogger()

# to see all data
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', 100)
pd.set_option('display.colheader_justify', 'left')

# if DataFrame kor broken
# tabulate.WIDE_CHARS_MODE=False

try:
    # For local test
    # chrome_options = Options()
    # chrome_options.add_experimental_option("detach", True)
    # chrome_options.add_argument("User-Agent:'application/json;charset=utf-8'")

    # For Ubuntu
    user_agent = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.50 Safari/537.36'
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('user-agent={0}'.format(user_agent))

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    # round info
    if (result := crawling_utils.without_kor(
            crawling_utils.crawling_element('https://finance.naver.com/marketindex/?tabSel=exchange#tab_section',
                                            '.section_exchange .round'))) != (open('./round.txt', 'r').read().rstrip()):
        # if True:
        driver.get("https://finance.naver.com/marketindex/exchangeList.naver")
        crawling_results = driver.find_elements(By.CLASS_NAME, 'tbl_area tbody tr')

        today = datetime.datetime.now().strftime('%Y-%m-%d')
        exchange_rate_lists = []
        for exchange_rate_info in crawling_results:
            exchange_data_array = exchange_rate_info.text.split()
            temp_list = exchange_data_array[len(exchange_data_array) - 6:]

            if not 'N/A' in temp_list:
                temp = []
                currency_name = crawling_utils.without_kor(exchange_rate_info.find_element(By.CLASS_NAME, 'tit').text)

                temp.append(today)
                temp.append(result)
                # temp.append("result")
                temp.append(currency_name)
                temp.append(temp_list[0].replace(',', ''))
                temp.append(temp_list[3].replace(',', ''))
                temp.append(temp_list[4].replace(',', ''))
                temp.append(temp_list[-1].replace(',', ''))
                exchange_rate_lists.append(temp)

        columns_basic_currency = ['날짜', '회차', '통화', '매매기준율', '송금 보내실때', '송금 받으실때', '미화환산율']
        # basic data complete
        basic_currency_df = pd.DataFrame(exchange_rate_lists, columns=columns_basic_currency)
        logger.debug(tabulate(basic_currency_df, headers='keys', tablefmt='pretty'))

        possible_arbitrage_list = []
        # calculate possible arbitrage list
        for idx, cases in enumerate(itertools.combinations(basic_currency_df['통화'], 2)):
            temp_arbitrage = []
            currency_1_send = basic_currency_df[basic_currency_df['통화'] == cases[0]]['송금 보내실때'].values
            currency_2_send = basic_currency_df[basic_currency_df['통화'] == cases[1]]['송금 보내실때'].values
            back_to_home_currency = basic_currency_df[basic_currency_df['통화'] == cases[1]][
                '송금 받으실때'].values
            # currency 1 / currency 2
            final_multiple = float(currency_1_send) / float(currency_2_send)
            # krw -> currency 1
            first_convert = round(float(1000000.0 / float(currency_1_send)), 2)
            # currency 1 -> currency 2
            second_convert = round(float(first_convert * final_multiple), 2)
            # currency 2 -> krw
            final_convert = round(second_convert * float(back_to_home_currency))
            final_profit = round(final_convert - 1000000.0)

            exchange_flow = 'KRW -> ' + cases[0] + ' -> ' + cases[1] + ' -> KRW'
            temp_arbitrage.append(exchange_flow)
            temp_arbitrage.append(str(format(first_convert, ',')) + '(' + cases[0] + ')')
            temp_arbitrage.append(str(format(second_convert, ',')) + '(' + cases[1] + ')')
            temp_arbitrage.append(format(final_convert, ','))
            temp_arbitrage.append(format(final_profit, ','))
            possible_arbitrage_list.append(temp_arbitrage)

        columns_possible_arbitrage = ['재정거래 흐름', '1차 환전', '2차 환전', '거래결과(KRW)', '최종수익(KRW)']
        possible_arbitrage_df = pd.DataFrame(possible_arbitrage_list, columns=columns_possible_arbitrage).sort_values(
            by='거래결과(KRW)', ascending=False)
        possible_arbitrage_df.reset_index(inplace=True, drop=True)
        # Arbitrage Calculation Compelte : possible_arbitrage_df

        logger.debug(possible_arbitrage_df[['재정거래 흐름', '거래결과(KRW)', '최종수익(KRW)']])

        # Saving total exchange rate data to excel
        excel_path = f'./oliver_util_package/excel/{today}_{result}회차.xlsx'
        # excel_path = './oliver_util_package/excel/' + today + '_회차.xlsx'
        with pd.ExcelWriter(excel_path) as writer:
            basic_currency_df.to_excel(writer, sheet_name='환율정보')
            possible_arbitrage_df.to_excel(writer, sheet_name='재정거래 시나리오')

        # Exchange rate News part
        news_list = crawling_utils.crawling_elements(
            'https://finance.naver.com/marketindex/news/newsList.naver?category=exchange', '.news_list li dt a')

        news_str_list = []
        news_start = '<tr><td><strong><a href="https://finance.naver.com'
        news_end = '</td></tr>'
        for idx, news in enumerate(news_list):
            news_detail = crawling_utils.crawling_element('https://finance.naver.com/' + news['href'],
                                                          'div .article_cont').split('. ', 2)
            temp = f'''
                    {news_start}{news['href']}" target="_blank"><h2>{news.text}</h2></a></strong></font><br/><h3>{'. '.join(news_detail[0:2])}...</h3>{news_end}
            '''
            news_str_list.append(temp)
            logger.debug(temp)

        # create html email body
        currency_info_str = f'<h3>{today} 고시 {result}회차의 환율정보</h3><br/>'
        # currency_info_str = f'<h3>{today} 고시회차 1의 환율정보</h3><br/>'
        possible_arbitrage_str = f'<h3>재정거래 시나리오 리스트</h3><br/>'
        body = currency_info_str + build_table(basic_currency_df[0:15], 'blue_dark', width="120px", font_size='medium',
                                               text_align='center',
                                               font_family='Open Sans, sans-serif'
                                               ) + '<br/><br/>' \
               + possible_arbitrage_str + build_table(possible_arbitrage_df[0:10], 'orange_dark', font_size='medium',
                                                      font_family='Open Sans, sans-serif',
                                                      conditions={
                                                          '최종수익(KRW)': {
                                                              'min': 0,
                                                              'max': 1,
                                                              'min_color': 'red',
                                                              'max_color': 'blue',
                                                          }}) + '<br/>'.join(news_str_list)

        # Sending email by html style
        email_utils.send_mail_html('lvsin@naver.com', f'{result}차 환율정보 및 재정거래 시나리오', body, excel_path)

        # round update
        # open('./round.txt', 'w').write("1")
        open('./round.txt', 'w').write(result)
    else:
        logger.info("Unchanged exchange rate data!")

except urle.HTTPError as e:
    logger.warning('HTTPError!\n', e)
except urle.URLError as e:
    logger.warning('The server could not be found!\n', e)
except Exception as e:
    logger.error("Error!\n", e)
finally:
    logger.info('Finally')
