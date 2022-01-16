from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import os
from copy import deepcopy
import re
import numpy as np
import nltk
from nltk.stem.wordnet import WordNetLemmatizer
from nltk import pos_tag
import mysql.connector
import asyncio
from datetime import datetime

    

# Instantiate options
opts = Options()
# opts.add_argument(" — headless") # Uncomment if the headless version needed
opts.binary_location = "C://Program Files//Google//Chrome//Application//chrome.exe"

# Set the location of the webdriver
chrome_driver = "C://Users//Abhigya Sodani//Downloads//chromedriver_win32//chromedriver.exe"

# Instantiate a webdriver
driver = webdriver.Chrome(options=opts, executable_path=chrome_driver)

# Load the HTML page
driver.get("http://beverlyhills.granicus.com/ViewPublisher.php?view_id=49")

# Parse processed webpage with BeautifulSoup
soup = BeautifulSoup(driver.page_source)
arch_meetings = str(soup)

#print(arch_meetings)
#p = re.compile('<td class="listItem"')
#
f=open("comments.txt","w")
arch_meetings= arch_meetings.split('<!--City Council Formal Meetings Table -->')[1].split("<!--City Council Closed Session -->")[0]

"""
all_upcoming_agendas = re.findall('<td class="listItemUpcoming" border-bottom:0px; headers="Name" scope="row">City Council Regular Meeting</td>',arch_meetings)

for i in all_upcoming_agendas:
    print(i)

input()
"""
all_agendas=re.findall('<td class="listItem" headers="Agenda .*"><a href=".*" target="_blank">Agenda</a></td>',arch_meetings)
dates=re.findall('<td class="listItem" headers="Date .*"><span style="display:none;">.*</span>.*</td>',arch_meetings)
agendas = []
all_dates=[]
for i in dates:
    
    all_dates.append(i.split("</span>")[1].split("</td>")[0].replace("&nbsp;"," "))
for i in all_agendas:
    agendas.append(i.split('href="//')[1].split('"')[0].replace("amp;",""))

print(agendas)

comments=[]
counter=0
for j in agendas:
    
    driver.get("http://"+j)   
    soup = BeautifulSoup(driver.page_source)
    soup = str(soup)
    data = re.findall('<span style="FONT-FAMILY: arial">Comment:.*<br/></span></span> <br/>',soup)

    #print(re.findall('<blockquote dir="ltr" style="MARGIN-RIGHT=0px;"><div><a ',soup))
    #print(data)
    for k in data:
        comment=k.split("Comment:")[1].split("<")[0].replace("xa0","")
        f.write(comment+"\n")
f.close()