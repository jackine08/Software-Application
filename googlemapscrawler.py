from tqdm import tqdm
from seleniumwire import webdriver
from time import sleep
import requests
import json
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
import re
from bs4 import BeautifulSoup


def google_reviews(store_list):

    #드라이버 실행
    options = webdriver.ChromeOptions()
    options.add_argument("user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")
    driver = webdriver.Chrome('./chromedriver',options=options)   #chromedriver 경로 지정!
    driver.get('https://www.google.co.kr/maps')
    sleep(1)

    # 리스트 형식으로 저장된 검색어 하나씩 검색
    for store in store_list:
        driver.get('https://www.google.co.kr/maps')
        result_list=[]
        sleep(1)
        query_input=driver.find_element(By.ID, 'searchboxinput')
        query_input.send_keys(store+'\n')
        
        # 검색결과가 같은지 확인
        sleep(3)
        check=input('일치하는 가게를 클릭 후 y를 눌러주세요(이외 멈춤)')
        if check.upper()=='Y':
            now_url=driver.current_url
        else:
            break
        
        # 리뷰로 이동
        more_btn=driver.find_element(By.XPATH, '/html/body/div[3]/div[9]/div[9]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]/div[1]/div[1]/div[2]/div/div[1]/div[2]/span[2]/span[1]/span')
        more_btn.click()
        views=int(''.join(more_btn.text[2:-1].split(',')))
        print(views)
        sleep(8)

        #스크롤
        element = driver.find_element(By.XPATH, '//*[@id="QA0Szd"]/div/div/div[1]/div[2]/div/div[1]/div/div/div[2]')
        
        for i in range(views//10):
            #더보기 클릭
            spread_review = driver.find_elements(By.XPATH, '//button[@class="w8nwRe kyuRq"]')
            print(len(spread_review))

            for j in range(len(spread_review)):
                isTrue = spread_review[j].is_displayed()    # 보이는 것인지를 확인
                print("Element is visible? " + str(isTrue))
                if isTrue:
                    spread_review[j].click()
                    print(str(j)+"th more button is clicked and wait 2 secs...")
                    sleep(1)
                    
            element.send_keys(Keys.END)
            sleep(2.5)

        # bs4 html 파싱
        html0 = driver.page_source
        soup = BeautifulSoup(html0, 'html.parser')

        #리뷰
        reviews =  soup.find_all('span',{'class':'wiI7pd'})
    
        #날짜
        date = soup.select('div.DU9Pgb > span.rsqaWe')
            
        #별점
        stars_string = soup.select('div.DU9Pgb > span.kvMYJc')
        stars = list()
        for s in stars_string:
            # 별표 n개 --> n만 저장
            tmp = s['aria-label'].replace('별표', '').replace('개', '')
            stars.append(tmp)
            
        # Save to CSV
        res_dict = list()
        for r, d, s in zip (reviews, date, stars):
                res_dict.append({
                    'STAR' : s,
                    'DATE' : d.text, 
                    'REVIEW' : r.text
                })

        res_df = pd.DataFrame(res_dict) 
        res_df.to_csv('./' + store + '_crawling_result.csv' ,index=False, encoding='utf-8-sig')

# 사용하기
store_list=['망상'] # 검색어 저장
google_reviews(store_list) #함수 실행

