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
def monthToNum(Month):
    return {
            'January': 1,
            'February': 2,
            'March': 3,
            'April': 4,
            'May': 5,
            'June': 6,
            'July': 7,
            'August': 8,
            'September': 9, 
            'October': 10,
            'November': 11,
            'December': 12
    }[Month]

def main():
   
    
    db = mysql.connector.connect(user='databse', password='sgbat2001',
                                host='34.132.108.122',
                                database='polls')
    cursor = db.cursor()
    add_poll = ("INSERT INTO polls (question, approve, no_opinion, disapprove, poll_date) VALUES (%(question)s, %(approve)s, %(no_opinion)s, %(disapprove)s, %(poll_date)s)")
    
    while(True):
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
                sentence = comment[1:len(comment)] #'There will be a book here.'
                sentence = sentence.lower()
                sentence = sentence.replace('.','')
                question_keywords = ['will', 'should']

                word_decomp = sentence.split()

                for i in range(len(word_decomp)):
                    if word_decomp[i] in question_keywords:
                        for x in question_keywords:
                            if word_decomp.count(x) >> 1:
                                
                                if pos_tag(word_decomp)[i+1][1] == 'VBN':
                                    word_decomp.insert(0, word_decomp[i])
                                    word_decomp.pop(i+1)
                                break
                            else:
                                word_decomp.insert(0, word_decomp[i])
                                word_decomp.pop(i+1)
                                break
                    else:
                        if i == len(word_decomp) - 2:
                            if word_decomp == sentence.split(' '): # If sentence unchanged
                                # Verb reduction:
                                for i in range(len(word_decomp)):
                                    if 'VB' in pos_tag(word_decomp)[i][1]:
                                        #print "BINGO"
                                        word_decomp[i] = WordNetLemmatizer().lemmatize(word_decomp[i],'v')
                                        #print "Verb reduction to present tense is required:"
                                word_decomp.insert(0, 'Should')

            
                for i in range(len(word_decomp)): # Cycle through all words
                    #print str(np.array(pos_tag([word_decomp[i]]))[0][1])
                    #print [word_decomp[i]]
                    if 'NP' in str(np.array(pos_tag([word_decomp[i]]))[0][1]): # Searches for a proper noun
                        word_decomp[i] = word_decomp[i].capitalize() # Capitalizes the proper noun
                
                    
                dot_to_que = word_decomp[len(word_decomp)-1].replace('.', '') # Deletes . at end of sentence if it is there
                word_decomp.insert(0,word_decomp[0].capitalize()) # Capitalizes first word of sentence
                word_decomp.pop(1) # Removes the possibly lowercase first word since the capitalized version has been inserted already
                question = (' ').join(word_decomp) # Create a string to reform the question instead of word by word
                if '?' not in question: # Ensures that ? is attached to end of the sentence
                    question = question + '?'
                date_arr=str(all_dates[counter]).replace(u"\xa0",u" ").replace(","," ").split(" ")
               
                insert_question = {'question':question, 'approve':0, 'no_opinion':0, 'disapprove':0, 'poll_date':datetime(int(date_arr[3]),int(monthToNum(date_arr[0])),int(date_arr[1])).strftime('%Y-%m-%d')}
            
               
                
                
                try:
                    
                    cursor.execute(add_poll, insert_question)
                    db.commit()
                except:
                    pass
            
            counter+=1
        cursor.close()
        db.close()
        #await asyncio.sleep(300)


    #nltk.download()
    #print(p.match(arch_meetings))  

    """
    <div><a name="agenda286111" class="Agenda Agenda1" href="https://beverlyhills.granicus.com/MediaPlayer.php?view_id=49&clip_id=4741&meta_id=286111" onclick="">MODIFYING THE PENALTY SURCHARGE FOR WATER USAGE IN EXCESS OF THE PROVISIONS OF THE STAGE D WATER CONSERVATION REQUIREMENTS.</a></div></td></tr></tbody></table></div><br><span style="FONT-FAMILY: arial"> <span style="FONT-FAMILY: arial">Comment: This resolution would replace the existing penalty surcharge resolution and reduce the penalty surcharge.Â <br/></span></span> <br/> 

    <blockquote dir="ltr" style="MARGIN-RIGHT=0px;"><div><a href="https://beverlyhills.granicus.com/MetaViewer.php?view_id=49&clip_id=4741&meta_id=286112"  name="document286112" class="Document Document2" onclick="">Item D-7</a></div><br>

    href=".*" name=".*" class="Document Document2" onclick="">
    .*</a></div><br>
    \n
    """
main()