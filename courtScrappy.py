#!/usr/bin/env python
# coding: utf-8

import urllib
import urllib3
from selenium import webdriver
import time
from bs4 import BeautifulSoup as bs
from selenium.webdriver.common.keys import Keys
import re
import pandas as pd
import unicodedata

DRIVER_PATH = './chromedriver.exe'
wd = webdriver.Chrome(executable_path=DRIVER_PATH)
time.sleep(5)
wd.get('https://portal.ncra.org/Sourcebook')
time.sleep(5)

def clickButton():
    wd.find_element_by_xpath("//input[@class='rcbInput radPreventDecorate']").click()
    time.sleep(5)
    x=0
    s = wd.find_elements_by_xpath(".//input[@class = 'rcbCheckBox'][ancestor::label[contains(., '')]]")
    for i in s:
        if x==70:
            break
        else:
            i.click()
            x+=1
    time.sleep(5)
    wd.find_element_by_xpath("//input[@value='Search']").click()
    
def getEmail():
    email_ar = []
    email = []
    email_temp = wd.page_source
    email_data = bs(email_temp, 'lxml')
    for strong_tag in email_data.find_all('tbody'):
        tester = strong_tag.find_all('a')
        for names in tester:
            pattern = re.compile(r'[m][a][i][l][t][o].+')
            for i in re.findall(pattern, str(names.get('href'))):
                email_ar.append(i)
    return email_ar

def getName():
    name_ar = []
    name_temp = wd.page_source
    name_data = bs(name_temp, 'lxml')
    for strong_tag in name_data.find_all('div', id="nameTitles2"):
        tester = strong_tag.find_all('b')
        for names in tester:
            clean_text = unicodedata.normalize("NFKD",names.text)
            name_ar.append(clean_text)
    return name_ar

def getState():
    address_ar = []
    address = []
    address_temp = wd.page_source
    address_data = bs(address_temp, 'html.parser')
    address_data.find_all('table')

    for strong_tag in address_data.find_all('table'):
        clean_text = unicodedata.normalize("NFKD",strong_tag.text)
        address.append(clean_text)

    test_address = re.findall(r'\,\s[A-Z]{2}\s', str(address))
    for i, k in enumerate(test_address):
        address_ar.append(test_address[i])
    return address_ar

def mainFunction():
    time.sleep(5)
    clickButton()
    x=0
    for i in range(0, 624):
        time.sleep(3)
        email = getEmail()
        for i,k in enumerate(email):
            emailArray.append(email[i])
        name = getName()
        for i,k in enumerate(name):
            nameArray.append(name[i])

        state = getState()
        for i, k in enumerate(state):
            stateArray.append(state[i])
        print("Iteration: " + str(x) + " " + "Email: " + str(len(emailArray)) + " " + "Name: " + str(len(nameArray)) + " " + "State: " + str(len(stateArray)))
        wd.find_element_by_xpath("//li[@class='next']").click()
        time.sleep(3)
        x+=1

emailArray = []
nameArray = []
stateArray = []
mainFunction()

nameDataframe = pd.DataFrame({'Name':nameArray})
nameDataframe["ID"] = range(0, len(nameDataframe))
nameDataframe = nameDataframe.set_index('ID')
nameDataframe['Name'] = nameDataframe['Name'].astype('object')
nameDataframe
nameDataframe[['Full_Name', 'Last_Name']] = nameDataframe['Name'].str.split(' ',n=1, expand=True)
nameDataframe = nameDataframe.drop(['Name'],1)
nameDataframe['Last_Name'] = nameDataframe['Last_Name'].str.replace(',',' ')
nameDataframe['Last_Name'] = nameDataframe['Last_Name'].str.replace(r'[A-Z]{2,3}','')
nameDataframe

emailDataFrame = pd.DataFrame({'Email':emailArray})
emailDataFrame["ID"] = range(0, len(emailDataFrame))
emailDataFrame = emailDataFrame.set_index('ID')
emailDataFrame[['Mailto', 'Mailing_List']] = emailDataFrame['Email'].str.split(':',n=1, expand=True)
emailDataFrame = emailDataFrame.drop(['Email'],1)
emailDataFrame = emailDataFrame.drop(['Mailto'],1)
emailDataFrame

newState = pd.DataFrame({'State':stateArray})
newState["ID"] = range(0, len(newState))
newState = newState.set_index('ID')
newState[['Delete', 'State_Letters']] = newState['State'].str.split(', ',n=2, expand=True)
newState = newState.drop(['Delete'],1)
newState = newState.drop(['State'],1)
newState

finalDataFrame = nameDataframe.merge(newState, how="left", on="ID")
dfToCSV = finalDataFrame.merge(emailDataFrame, how="left", on="ID")
dfToCSV

dfToCSV.to_csv("Court_reporters.csv", sep=',', columns=['Full_Name','Last_Name','State_Letters','Mailing_List'], encoding='utf-8')
