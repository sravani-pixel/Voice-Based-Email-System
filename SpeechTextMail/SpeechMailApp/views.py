from django.shortcuts import render
from django.template import RequestContext
from django.contrib import messages
import pymysql
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage
import datetime
import os
from datetime import date
from gtts import gTTS
import os
from playsound import playsound
import speech_recognition as sr
import re
import traceback
from django.http import JsonResponse
import traceback

global uname, password, index
index = "0"
file = "good"

def texttospeech(text, filename):
    filename = filename + '.mp3'
    flag = True
    while flag:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            tts.save(filename)
            flag = False
        except:
            print('Trying again')
    playsound(filename)
    os.remove(filename)
    return

def speechtotext(duration):
    global i, addr, passwrd
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source, duration=1)
        # texttospeech("speak", file + i)
        # i = i + str(1)
        playsound('speak.mp3')
        audio = r.listen(source, phrase_time_limit=duration)
    try:
        response = r.recognize_google(audio)
    except:
        traceback.print_exc()
        response = 'N'
    return response

def convert_special_char(text):
    temp=text
    special_chars = ['dot','underscore','dollar','hash','star','plus','minus','space','dash','at']
    for character in special_chars:
        while(True):
            pos=temp.find(character)
            if pos == -1:
                break
            else :
                if character == 'dot':
                    temp=temp.replace('dot','.')
                elif character == 'underscore':
                    temp=temp.replace('underscore','_')
                elif character == 'dollar':
                    temp=temp.replace('dollar','$')
                elif character == 'hash':
                    temp=temp.replace('hash','#')
                elif character == 'star':
                    temp=temp.replace('star','*')
                elif character == 'plus':
                    temp=temp.replace('plus','+')
                elif character == 'minus':
                    temp=temp.replace('minus','-')
                elif character == 'space':
                    temp = temp.replace('space', '')
                elif character == 'dash':
                    temp=temp.replace('dash','-')
                elif character == 'at':
                    temp=temp.replace('at','@')    
    return temp

def authenticateUser(username, password):
    auth = False
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
    with con:
        cur = con.cursor()
        cur.execute("select * FROM signup")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == username and row[1] == password:
                auth = True
                break
    return auth

def UserLogin(request):
    if request.method == 'GET':
        global uname, password, file, index
        msg = "Invalid Login Details. Please try again."
        text1 = "Welcome to our Voice Based Email Portal. Login with your email account to continue. "
        texttospeech(text1, file + index)
        index = index + str(1)
        flag = True
        while (flag):
            texttospeech("Enter your Email", file + index)
            index = index + str(1)
            uname = speechtotext(5)
            if uname != 'no':
                texttospeech("You meant " + uname + " say email is correct to confirm or email is wrong to enter again", file + index)
                index = index + str(1)
                say = speechtotext(5)
                print("===================="+say)
                if say.lower() == 'email is correct':
                    flag = False
            else:
                texttospeech("could not understand what you meant:", file + index)
                index = index + str(1)
        uname = uname.strip()
        uname = uname.replace(' ', '')
        uname = uname.lower()
        uname = convert_special_char(uname)
        flag = True
        while (flag):
            texttospeech("Enter your password", file + index)
            index = index + str(1)
            password = speechtotext(5)
            if password != 'no':
                texttospeech("You meant " + password + " say password is correct to confirm or password is wrong to enter again", file + index)
                index = index + str(1)
                say = speechtotext(3)
                if say.lower() == 'password is correct':
                    flag = False
            else:
                texttospeech("could not understand what you meant:", file + index)
                index = index + str(1)
        password = password.strip()
        password = password.replace(' ', '')
        password = password.lower()
        password = convert_special_char(password)
        print(uname+" === "+password)
        if authenticateUser(uname, password) == True:
            msg = "Congratulations. You have logged in successfully. You will now be redirected to options page."
            texttospeech(msg, file + index)
            index = index + str(1)
            context= {'data':"Welcome "+uname}
            return render(request, 'UserScreen.html', context)
        else:
            texttospeech(msg, file + index)
            index = index + str(1)
            context= {'data':msg}
            return render(request, 'UserLogin.html', context)

def indexPage(request):
    if request.method == 'GET':
       return render(request, 'index.html', {})

def Signup(request):
    if request.method == 'GET':
       return render(request, 'Signup.html', {})

def SignupAction(request):
    if request.method == 'POST':
        username = request.POST.get('t1', False)
        password = request.POST.get('t2', False)
        contact = request.POST.get('t3', False)
        gender = request.POST.get('t4', False)
        address = request.POST.get('t5', False)
        
        status = 'none'
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select email_id from signup where email_id = '"+username+"'")
            rows = cur.fetchall()
            for row in rows:
                if row[0] == email:
                    status = 'Given Username already exists'
                    break
        if status == 'none':
            db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
            db_cursor = db_connection.cursor()
            student_sql_query = "INSERT INTO signup(email_id,password,contact_no,gender,address) VALUES('"+username+"','"+password+"','"+contact+"','"+gender+"','"+address+"')"
            db_cursor.execute(student_sql_query)
            db_connection.commit()
            print(db_cursor.rowcount, "Record Inserted")
            if db_cursor.rowcount == 1:
                status = 'Signup Process Completed'
        context= {'data':status}
        return render(request, 'Signup.html', context)

def ViewMails(request):
    if request.method == 'GET':
        global uname
        output = '<table border=1><tr>'
        output+='<td><font size="" color="black">Mail ID</td>'
        output+='<td><font size="" color="black">Receiver Mail</td>'
        output+='<td><font size="" color="black">Subject</td>'
        output+='<td><font size="" color="black">Message</td>'
        output+='<td><font size="" color="black">Sender</td>'
        output+='<td><font size="" color="black">Date</td>'
        output+='<td><font size="" color="black">Click Here to Readout</td></tr>'
        rank = []
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select * FROM mail where receiver='"+uname+"'")
            rows = cur.fetchall()
            for row in rows:
                mail_id = str(row[0])
                receiver = row[1]
                subject = row[2]
                message = row[3]
                sender = row[4]
                dd = row[5]
                status = row[6]
                size = 3
                if status == 'Pending':
                    size=4
                output+='<tr>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(mail_id)+'</td>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(receiver)+'</td>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(subject)+'</td>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(message)+'</td>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(sender)+'</td>'
                output+='<td><font size="'+str(size)+'" color="black">'+str(dd)+'</td>'
                output+='<td><a href=\'Readout?t1='+str(mail_id)+'\'><font size=3 color=black>Readout</font></a></td></tr>'                
        output += "</table><br/><br/><br/>"
        context= {'data':output}
        return render(request, 'UserScreen.html', context)

def Readout(request):
    if request.method == 'GET':
        global index
        mail_id = request.GET.get('t1', False)
        message = ""
        con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
        with con:
            cur = con.cursor()
            cur.execute("select sender, email_date, subject, message FROM mail where mail_id='"+mail_id+"'")
            rows = cur.fetchall()
            for row in rows:
                message = "Sender Email is "+row[0]+" sent Email on "+row[1]+" Subject is "+ row[2]+" Message Details "+row[3]
        db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
        db_cursor = db_connection.cursor()
        student_sql_query = "update mail set status='viewed' where mail_id='"+mail_id+"'"
        db_cursor.execute(student_sql_query)
        texttospeech(message, file + index)
        index = index + str(1)
        return JsonResponse({'result': 'success'})

def receiverExists(receiver):
    flag = False
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
    mail_id  = 0
    with con:
        cur = con.cursor()
        cur.execute("select email_id FROM signup")
        rows = cur.fetchall()
        for row in rows:
            if row[0] == receiver:
                flag = True
                break
    return flag            

def sendMail(uname, receiver, subject, message):
    flag = False
    today = date.today()
    con = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
    mail_id  = 0
    with con:
        cur = con.cursor()
        cur.execute("select max(mail_id) FROM mail")
        rows = cur.fetchall()
        for row in rows:
            mail_id = row[0]
    if mail_id is not None:
        mail_id = mail_id + 1
    else:
        mail_id = 1
    db_connection = pymysql.connect(host='127.0.0.1',port = 3306,user = 'root', password = 'root', database = 'VoiceMail',charset='utf8')
    db_cursor = db_connection.cursor()
    student_sql_query = "INSERT INTO mail(mail_id,receiver,subject,message,sender,email_date,status) VALUES('"+str(mail_id)+"','"+receiver+"','"+subject+"','"+message+"','"+uname+"','"+str(today)+"','Pending')"
    db_cursor.execute(student_sql_query)
    db_connection.commit()
    print(db_cursor.rowcount, "Record Inserted")
    if db_cursor.rowcount == 1:
        flag = True
    return flag    

def ComposeMails(request):
    if request.method == 'GET':
        global uname, file, index
        receiver = ""
        subject = ""
        message = ""
        msg = "Invalid Receiver Mail"
        flag = True
        while (flag):
            texttospeech("Enter Receiver Email", file + index)
            index = index + str(1)
            receiver = speechtotext(5)
            if receiver != 'no':
                texttospeech("You meant " + receiver + " say receiver is correct to confirm or receiver is wrong to enter again", file + index)
                index = index + str(1)
                say = speechtotext(3)
                if say.lower() == 'receiver is correct':
                    receiver = receiver.strip()
                    receiver = receiver.replace(' ', '')
                    receiver = receiver.lower()
                    receiver = convert_special_char(receiver)
                    if receiverExists(receiver) == True:
                        flag = False
                    else:
                        texttospeech("Receiver "+receiver+" Does not exists. Try again", file + index)
                        index = index + str(1)
            else:
                texttospeech("could not understand what you meant:", file + index)
                index = index + str(1)        
        flag = True
        while (flag):
            texttospeech("Enter Subject Details ", file + index)
            index = index + str(1)
            subject = speechtotext(4)
            if subject != 'no':
                texttospeech("You meant " + subject + " as subject say subject is correct to confirm or subject is wrong to enter again", file + index)
                index = index + str(1)
                say = speechtotext(3)
                if say.lower() == 'subject is correct':
                    flag = False
            else:
                texttospeech("could not understand what you meant:", file + index)
                index = index + str(1)
        flag = True
        while (flag):
            texttospeech("Enter Message Details ", file + index)
            index = index + str(1)
            message = speechtotext(5)
            if message != 'no':
                texttospeech("You meant " + message + " as message say message is correct to confirm or message is wrong to enter again", file + index)
                index = index + str(1)
                say = speechtotext(3)
                if say.lower() == 'message is correct':
                    flag = False
            else:
                texttospeech("could not understand what you meant:", file + index)
                index = index + str(1)
        if sendMail(uname, receiver, subject, message) == True:
            msg = "Mail successfully sent to "+receiver
        else:
            msg = "Error in sending mail"
        texttospeech(msg, file + index)
        index = index + str(1)
        context= {'data':msg}
        return render(request, 'UserScreen.html', context)    

