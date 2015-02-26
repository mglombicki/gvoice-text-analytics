"""
Google Voice Text Analytics
by Michael Glombicki
Created 8/30/2013
"""

import os
import lxml.html,lxml.etree
import operator
import time
import csv

#The google takeout "Calls" folder
calls_folder="C:\Users\<user_name>\Downloads\user_name@gmail.com-takeout\user_name@gmail.com-takeout\Voice\Calls"

def analyze(calls_folder):
    for dirname, dirnames, filenames in os.walk(calls_folder):
        file_count=0
        thread_freq={}
        person_messages={}
        conversation_messages=[]
        num_initiated=0
        num_not_initiated=0
        total_sent=0
        total_recieved=0

        print "Analyzing",len(filenames),"files"

        # print path to all filenames.
        for filename in filenames:
            if ".html" in filename and "_-_Text_-_" in filename:
                name=filename.split("_-_")[0]
                if name in thread_freq.keys():
                    thread_freq[name]+=1
                else:
                    thread_freq[name]=1
                file_count+=1
                sent,recieved,initiated,response_times=read_conversation(os.path.join(dirname, filename))
                total_sent+=sent
                total_recieved+=recieved
                conversation_messages.append(sent+recieved)
                if (initiated):
                    num_initiated+=1
                else:
                    num_not_initiated+=1
                if name in person_messages.keys():
                    person_messages[name][0]+=sent
                    person_messages[name][1]+=recieved
                    person_messages[name][2]+=0
                else:
                    person_messages[name]=[sent,recieved,0]
                
        print sorted(person_messages.iteritems(), key=operator.itemgetter(1))
        #print sorted(thread_freq.iteritems(), key=operator.itemgetter(1))
        with open("names.csv", 'wb') as csvfile:
            row1=[]
            row2=[]
            row3=[]
            for item in sorted(person_messages.iteritems(), key=operator.itemgetter(1)):
                writer = csv.writer(csvfile)
                row1.append(item[0])
                row2.append(item[1][0])
                row3.append(item[1][1])
            writer.writerow(row1)
            writer.writerow(row2)
            writer.writerow(row3)

        print "Found",file_count,"text message conversations with",len(thread_freq.keys()),"different phone numbers"
        print "of which you initiated", num_initiated
        print ""
        print "The conversations contained",total_sent+total_recieved,"total messages (sent and recieved)"
        print "Of those, you sent:",total_sent,"and recieved:",total_recieved
        print "Your average conversation contained",average(conversation_messages),"messages"


def read_conversation(filename):
    sent=0
    recieved=0
    initiated=False
    response_times=[]
    
    conversation=open(filename)
    doc= lxml.html.document_fromstring(conversation.read())
    messages = doc.xpath("//div[@class='message']")

    first=True
    previous_time=None
    responding=False
    for message in messages:
##        print lxml.etree.tostring(message)
##        sender=message.find("cite").find("a").find("span").text
        sender=message.xpath('./cite/a')[0].getchildren()[0].text
        message_time=message.getchildren()[0].get("title")#.split(".")[0]#throws away time zone info
        if sender=="Me":
            sent+=1
            if first:
                initiated=True
                first=False
            if responding:
                pass
                #response_times.append(time-previous_time)
            responding=False
        else:
            recieved+=1
            responding=True
            #previous_time=time.strptime(message_time, "%Y-%m-%dT%H:%M:%S")
        first=False
        
    return (sent,recieved,initiated,response_times)

def average(numbers):
    return sum(numbers)/len(numbers)
        



if __name__ == "__main__":
    analyze(calls_folder)
