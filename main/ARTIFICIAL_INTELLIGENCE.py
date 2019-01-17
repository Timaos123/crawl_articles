# -*- coding: utf-8 -*-
"""
Created on Thu Sep 27 19:05:36 2018

@author: J

需求文件：
pdf.py同一目录下的record.txt用于记录下载中断位置，初始化里面为0
pdf.py同一目录下的file空文件夹

运行环境：
python3.6
Google Chrome v67(配上TemperMonkey上的下载插件，而且不能事先打开浏览器窗口)
chromedriver v2.4.1

第三方库：
selenium
BeautifulSoup

"""

import re
import os
import time 
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver import ActionChains
from bs4 import BeautifulSoup

#driver = webdriver.PhantomJS(executable_path = r"D:\Anaconda3\Scripts")
class PDF:
    def __init__(self):
        self.download_dir="C:\\Users\\Administrator\\Desktop\\crawl_article\\workspace\\crawlArticle\\main\\artificial_intelligence"#绝对地址
        self.base_url='https://www.sciencedirect.com'
        self.url='https://www.sciencedirect.com/journal/artificial-intelligence/issues'
        options = webdriver.ChromeOptions()
        profile = {"plugins.plugins_list": [{"enabled": False, "name": "Chrome PDF Viewer"}],
                   "download.default_directory": self.download_dir}#文件保存路径
        options.add_experimental_option("prefs", profile)
        options.add_argument("user-data-dir=C:\\Users\\20143\\AppData\\Local\\Google\\Chrome\\User Data")#谷歌用户数据保存路径
      
        self.driver = webdriver.Chrome(chrome_options=options)
        self.start_year=2010
        self.end_year=2018
        
    def get_url(self):      #获取pdf的年份、名字和下载链接，存储到文件中
        self.driver.get(self.url)
        for i in range(1,self.end_year-self.start_year+1):
            
            elem_id='0-accordion-tab-'+str(i)
            print('clicking '+str(self.end_year-i)+' button')
            elem=self.driver.find_element_by_id(elem_id)
            ActionChains(self.driver).move_to_element(elem).perform() 
            elem.send_keys(Keys.ENTER)

        time.sleep(10)
        soup = BeautifulSoup(self.driver.page_source,"lxml")

        linklst = []
        for x in soup.find_all('a', href = re.compile('vol')):
            link = x.get('href')
            if link:
                linklst.append(self.base_url+link)
                print('---------------------------get vol url-----------------')
                print(self.base_url+link)
        del linklst[0]
        with open('url.txt','w+',encoding='utf-8') as file:
            for link in linklst:
                try:
                    self.driver.get(link)
                    time.sleep(5*np.random.random())
                    pdf_links=self.driver.find_elements_by_class_name('pdf-download')
                    year=self.driver.find_elements_by_class_name('js-issue-status')[0].text[-5:-1]
                    names=self.driver.find_elements_by_class_name('js-article-title')    
                    vol=self.driver.find_elements_by_class_name('js-vol-issue')[0].text
                    print('getting '+vol)
                    
                    soup = BeautifulSoup(self.driver.page_source,"lxml")
                    pdf_links = []
                    for x in soup.find_all('a', class_ = re.compile('pdf\-download')):
                        link = x.get('href')
                        if link:
                            pdf_links.append(link)
                            print('------------------get pdf url------------')
                            print(link)
                            
                    for i in range(len(pdf_links)):
                        pdf_link=pdf_links[i]
                        if '.pdf' not in pdf_link:
                            print('----------------error Url---------------')
                            print(pdf_link)
                            break
                        name=names[i].text
                        if('Editorial' in name):
                            name+=vol
                        name=name.replace(' ','_')
                        name=name.replace(':','')
                        name=name.replace('/','')
                        name=name.replace(',','')
                        name=name.replace('"','')
                        name=name.replace('\'','')
                        name=name.replace('?','')
                        name=name.replace('|','')
                        name=name.replace('<','')
                        name=name.replace('>','')
                        name=name.replace('*','')
                        name=name.replace('...','')
                        name=name.replace('!,','')
    
                        if pdf_link:
                            file.write(year+' '+name+'.pdf'+' '+pdf_link+'\n')
                except Exception as e:
                    print(e)    
                    continue
            print('----------------------end of getting url-------------------')
            print('链接爬取完成，可以注释掉该函数对应代码')
        
    def download(self):      #读取文件中的pdf链接进行下载
        file=open('url.txt','r',encoding='utf-8')
        lines=file.readlines()
        file.close()
        count=0
        os.chdir(self.download_dir)
        print('----------------------start downloading----------------')
        for line in lines:
            
            count+=1
            
            line_split=line.split(' ')
            year=line_split[0]
            name=line_split[1]
            name=name.replace(':','')
            name=name.replace('/','')
            name=name.replace(',','')
            name=name.replace('\"','')
            name=name.replace('\'','')
            name=name.replace('?','')
            name=name.replace('¿','')
            name=name.replace('|','')
            name=name.replace('<','')
            name=name.replace('>','')
            name=name.replace('*','')
            name=name.replace('...','')
            name=name.replace('!,','')
            if('Editorial' in name):
                continue
            url=self.base_url+line_split[2]
            print('--------------downloading No.'+str(count)+' pdf------------')
            print(url)
            
#             self.driver.get(url)
#             old_name=self.driver.current_url.split('pid=')[1]
#             
#             time.sleep(6)
#             print(old_name+'------>'+year+'_'+name+'.pdf')
#             os.rename(old_name, year+'_'+name+'.pdf')

            try:
                self.driver.get(url)
                old_name=url.split('pid=')[1].strip()
                print(old_name+'------>'+year+'_'+name)
                time.sleep(10)
                os.rename(old_name, year+'_'+name)
            except FileNotFoundError as e:
                print(e)
                time.sleep(360)
                try:
                    os.rename(old_name, year+'_'+name)
                except:
                    record=open('../record.txt','a+')
                    record.write(str(count))
                    record.close()
                    break
                continue
            except Exception as e:
                print('------------Error-------------')
                print(e)
                
                record=open('../record.txt','a+')
                record.write(str(count))
                record.close()
                print('interrupt while downloading No.'+str(count))
                break
        
if __name__=='__main__':
    pdf=PDF()
#     pdf.get_url()       #先运行这句代码获取url，url获取完后注释掉这句代码
    pdf.download()      #再运行这句代码下载pdf，下载中断后重新运行程序从端点继续下载，注意要把上一句代码注释掉