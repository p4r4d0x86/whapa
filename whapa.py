﻿#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from colorama import init, Fore
from BeautifulSoup import BeautifulStoneSoup
from configparser import ConfigParser
import cgi
import distutils.dir_util
import argparse
import sqlite3
import os
import time
import zlib
import sys

# Define global variable
arg_user = ""
arg_group = ""
report_var = ""             # Save args.report valor
report_html = ""
version = "0.5"


def banner():
    """ Function Banner """
    print """
     __      __.__          __________         
    /  \    /  \  |__ _____ \______   \_____   
    \   \/\/   /  |  \\\\__  \ |     ___/\__  \  
     \        /|   Y  \/ __ \|    |     / __ \_
      \__/\  / |___|  (____  /____|    (____  /
           \/       \/     \/               \/ 
    ---------- Whatsapp Parser v""" + version + """ -----------
    """


def help():
    """ Function show help """
    print """    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Usage: python whapa.py -h (for help)
    """


def decrypt(db_file, key_file):
    """ Function decrypt Crypt12 Database """
    try:
        with open(key_file, "rb") as fh:
            key_data = fh.read()

        key = key_data[126:]
        with open(db_file, "rb") as fh:
            db_data = fh.read()

        iv = db_data[51:67]
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open("msgstore.db", "wb") as fh:
            fh.write(zlib.decompress(aes.decrypt(db_data[67:-20])))

        print db_file + " decrypted, msgstore.db created."
    except Exception as e:
        print "An error has ocurred decrypting the Database:", e


def db_connect(db):
    """ Function connect to Database"""
    if os.path.exists(db):
        try:
            with sqlite3.connect(db) as conn:
                global cursor
                cursor = conn.cursor()
            print args.database, "Database connected\n"
            return cursor
        except Exception as e:
            print "Error connecting to Database, ", e
    else:
        print "msgstore database doesn't exist"
        exit()


def reply(txt):
    """ Function look out answer messages """
    sql_reply_str = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, " \
                "remote_resource, edit_version, thumb_image, recipient_count, raw_data, starred, quoted_row_id FROM messages WHERE key_id IN (SELECT messages_quotes.key_id FROM messages " \
                "INNER JOIN messages_quotes ON messages.quoted_row_id = messages_quotes._id WHERE messages.quoted_row_id = " + str(txt) + ")"
    sql_answer = cursor.execute(sql_reply_str)
    rep = sql_answer.fetchone()
    ans = ""
    reply_msj = ""
    if rep is not None:  # Message not deleted
        if int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "g.us":  # I send message to group
            ans = "Me"
            if report_var == 'EN':
                reply_msj = "<font color=\"#FF0000\" > Me </font>"
            elif report_var == 'ES':
                reply_msj = "<font color=\"#FF0000\" > Yo </font>"
        elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":  # I send message to somebody
            ans = "Me"
            if report_var == 'EN':
                reply_msj = "<font color=\"#FF0000\" > Me </font>"
            elif report_var == 'ES':
                reply_msj = "<font color=\"#FF0000\" > Yo </font>"
        elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "broadcast":  # I send broadcast
            ans = "Me"
            if report_var == 'EN':
                reply_msj = "<font color=\"#FF0000\" > Me </font>"
            elif report_var == 'ES':
                reply_msj = "<font color=\"#FF0000\" > Yo </font>"
        elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "g.us":  # Group send me a message
            ans = (str(rep[15]).split('@'))[0]
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj = "<font color=\"#FF0000\" > " + (str(rep[15]).split('@'))[0] + " " + gets_name(rep[15]) + "</font>"
        elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":  # Somebody sends me a message (normal and broadcast)
            ans = (str(rep[0]).split('@'))[0]
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj = "<font color=\"#FF0000\" > " + (str(rep[0]).split('@'))[0] + " " + gets_name(rep[0]) + "</font>"
        elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "broadcast":  # Somebody posts a Status
            ans = (str(rep[15]).split('@'))[0]
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj = "<font color=\"#FF0000\" > " + (str(rep[15]).split('@'))[0] + " " + gets_name(rep[15]) + "</font>"

        if int(rep[8]) == 0:  # media_wa_type 0, text message
            ans += Fore.RED + " - Message: " + Fore.RESET + rep[4]
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + cgi.escape(rep[4])

        elif int(rep[8]) == 1:  # media_wa_type 1, Image
            chain = str(rep[17]).split('w')[0]
            i = chain.rfind("Media/")
            b = len(chain)
            if i == -1:  # Image doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = "/" + (str(rep[17]))[i:b]
            if rep[11]:  # media_caption
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11]
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8') + " - " + cgi.escape(rep[11]) + "<br> <a href=\".." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='.." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8') + "<br> <a href=\".." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='.." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 2:  # media_wa_type 2, Audio
            chain = str(rep[17]).split('w')[0]
            i = chain.rfind("Media/")
            b = len(chain)
            if i == -1:  # Audio doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = "/" + (str(rep[17]))[i:b]
            ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9]))) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12])
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + thumb.decode('utf-8') + " " + size_file(int(rep[9])) + " - " + duration_file(rep[12]) + "<br></br><audio controls> <source src=\".." + thumb.decode('utf-8') + "\" type=\"" + rep[7] + "\"</audio>"

        elif int(rep[8]) == 3:  # media_wa_type 3 Video
            chain = str(rep[17]).split('w')[0]
            i = chain.rfind("Media/")
            b = len(chain)
            if i == -1:  # Video doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = "/" + (str(rep[17]))[i:b]
            if rep[11]:  # media_caption
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11]
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8') + " - " + cgi.escape(rep[11])
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb
                reply_msj += "<br>" + thumb.decode('utf-8')
                if (report_var == 'EN') or (report_var == 'ES'):
                    ans += Fore.RED + " - Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9]))) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12])
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += " " + size_file(int(rep[9])) + " - " + duration_file(rep[12]) + "<br/> <a href=\".." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='.." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 4:  # media_wa_type 4, Contact
            ans += Fore.RED + " - Name: " + Fore.RESET + rep[10] + Fore.RED + " - Type:" + Fore.RESET + " Contact vCard"
            if report_var == 'EN':
                reply_msj += "<br>" + cgi.escape(rep[10]) + " &#9742;  Contact vCard"
            if report_var == 'ES':
                reply_msj += "<br>" + cgi.escape(rep[10]) + " &#9742;  Contacto vCard"

        elif int(rep[8]) == 5:  # media_wa_type 5, Location
            if rep[6]:  # media_url exists
                if rep[10]:  # media_name exists
                    ans += Fore.RED + " - Url: " + Fore.RESET + rep[6] + Fore.RED + " - Name: " + Fore.RESET + rep[10]
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + cgi.escape(rep[6]) + " - " + cgi.escape(rep[10])
                else:
                    ans += Fore.RED + " - Url: " + Fore.RESET + rep[6]
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + cgi.escape(rep[6])
            else:
                if rep[10]:
                    ans += Fore.RED + "Name: " + Fore.RESET + rep[10]
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + cgi.escape(rep[10])
            ans += Fore.RED + " - Type:" + Fore.RESET + " Location" + Fore.RED + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.RED + " - Long: " + Fore.RESET + str(rep[14])
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "(" + str(rep[13]) + "," + str(rep[14]) + ")" + "<br><a href=\"https://www.google.es/maps/search/(" + str(rep[13]) + "," + str(rep[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(rep[13]) + "," + str(rep[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(rep[13]) + "," + str(rep[14]) + "&sensor=false\"/></a>"

        elif int(rep[8]) == 8:  # media_wa_type 8, Audio / Video Call
            ans += Fore.RED + " - Call: " + Fore.RESET + rep[11] + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12])
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + "&#128222; " + str(rep[11]).capitalize() + " " + duration_file(rep[12])

        elif int(rep[8]) == 9:  # media_wa_type 9, Application
            chain = str(rep[17]).split('w')[0]
            i = chain.rfind("Media/")
            b = len(chain)
            if i == -1:  # Image doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = "/" + chain[i:b]
            if rep[11]:  # media_caption
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11]
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8') + " - " + cgi.escape(rep[11])
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8')
            if int(rep[12]) > 0:
                ans += Fore.RED + " - Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.RED + " - Pages: " + Fore.RESET + str(rep[12])
                if report_var == 'EN':
                    reply_msj += " " + size_file(int(rep[9])) + " - " + str(rep[12]) + " Pages"
                if report_var == 'ES':
                    reply_msj += " " + size_file(int(rep[9])) + " - " + str(rep[12]) + " Páginas".decode('utf-8')
            else:
                ans += Fore.RED + " - Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9]))
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += " " + size_file(int(rep[9]))
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br> <a href=\"." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='.." + thumb.decode('utf-8') + ".jpg' width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 10:  # media_wa_type 10, Video/Audio call lost
            ans += Fore.RED + " - Message: " + Fore.RESET + " Missed " + rep[11] + " call"
            if report_var == 'EN':
                reply_msj += "<br>" + "&#128222; Missed" + str(rep[11]).capitalize()
            if report_var == 'ES':
                reply_msj += "<br>" + "&#128222; " + str(rep[11]).capitalize() + " llamada perdida"

        elif int(rep[8]) == 13:  # media_wa_type 13 Gif
            chain = str(rep[17]).split('w')[0]
            i = chain.rfind("Media/")
            b = len(chain)
            if i == -1:  # Video doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = "/" + (str(rep[17]))[i:b]
            if rep[11]:  # media_caption
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11]
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8') + " - " + cgi.escape(rep[11])
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb.decode('utf-8')
            ans += Fore.RED + " - Type: " + Fore.RESET + "Gif" + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12])
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += " - Gif - " + size_file(int(rep[9])) + " " + duration_file(rep[12]) + "<br> <a href=\".." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='.." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 15:  # media_wa_type 15, Deleted Object
            if int(rep[16]) == 5:  # edit_version 5, deleted for me
                ans += Fore.RED + " - Message:" + Fore.RESET + " Message deleted for Me"
                if report_var == 'EN':
                    reply_msj += "<br>" + "Message deleted for Me"
                if report_var == 'ES':
                    reply_msj += "<br>" + "Mensaje eliminado para mí".decode('utf-8')
            elif int(rep[16]) == 7:  # edit_version 7, deleted for all
                ans += Fore.RED + " - Message:" + Fore.RESET + " Message deleted for all participants"
                if report_var == 'EN':
                    reply_msj += "<br>" + "Message deleted for all participants"
                if report_var == 'ES':
                    reply_msj += "<br>" + "Mensaje eliminado para todos los destinatarios"

        elif int(rep[8]) == 16:  # media_wa_type 16, Share location
            ans += Fore.RED + " - Type:" + Fore.RESET + " Real time location " + Fore.RED + "- Caption: " + Fore.RESET + rep[11] + Fore.RED + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.RED + " - Long: " + Fore.RESET + str(rep[14]) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])
            if report_var == 'EN':
                reply_msj += "<br>" + "Real time location (" + str(rep[13]) + "," + str(rep[14]) + ") - " + cgi.escape(rep[11]) + " <br><a href=\"https://www.google.es/maps/search/(" + str(rep[13]) + "," + str(rep[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(rep[13]) + "," + str(rep[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(rep[13]) + "," + str(rep[14]) + "&sensor=false\"/></a>"
            if report_var == 'ES':
                reply_msj += "<br>" + "Ubicación en tiempo real(".decode('utf-8') + str(rep[13]) + "," + str(rep[14]) + ") - " + cgi.escape(rep[11]) + " <br><a href=\"https://www.google.es/maps/search/(" + str(rep[13]) + "," + str(rep[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(rep[13]) + "," + str(rep[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(rep[13]) + "," + str(rep[14]) + "&sensor=false\"/></a>"

        ans += Fore.RED + " - Timestamp: " + Fore.RESET + time.strftime('%d-%m-%Y %H:%M', time.localtime(int(rep[5]) / 1000))
        if (report_var == 'EN') or (report_var == 'ES'):
            reply_msj += "</br><b><small>" + time.strftime('%d-%m-%Y %H:%M', time.localtime(int(rep[5]) / 1000)) + "</small></b>"

    else:  # Deleted Message
        ans = "Deleted message"
        if report_var == 'EN':
            reply_msj = "Deleted message"
        if report_var == 'ES':
            reply_msj = "Mensaje eliminado"

    return ans, reply_msj


def status(st):
    """ Function message status"""
    if st == 0 or st == 5:  # 0 for me and 5 for target
        return "Received", "&#10004;&#10004;"
    elif st == 4:
        return Fore.RED + "Waiting in server" + Fore.RESET, "&#10004;"
    elif st == 6:
        return Fore.YELLOW + "System message" + Fore.RESET, "&#128187;"
    elif st == 8 or st == 10:
        return Fore.BLUE + "Audio played" + Fore.RESET, "&#9989;"  # 10 for me and 8 for target
    elif st == 13:
        return Fore.BLUE + "Seen" + Fore.RESET, "&#9989;"
    else:
        return st


def size_file(obj):
    """ Function objects size"""
    if obj > 1048576:
        obj = "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
    else:
        obj = "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"
    return obj


def duration_file(obj):
    """ Function duration tiMe"""
    hour = (int(obj / 3600))
    minu = int((obj - (hour * 3600)) / 60)
    seco = obj - ((hour * 3600) + (minu * 60))
    if obj >= 3600:
        obj = (str(hour) + "h " + str(minu) + "m " + str(seco) + "s")
    elif 60 < obj < 3600:
        obj = (str(minu) + "m " + str(seco) + "s")
    else:
        obj = (str(seco) + "s")
    return obj


def names(obj):
    """ Function saves a name list if exits wa.db"""
    global names_dict
    names_dict = {}  # jid : display_name
    if os.path.exists(obj):
        try:
            with sqlite3.connect(obj) as conn:
                cursor_name = conn.cursor()
                sql_names = "SELECT jid, display_name FROM wa_contacts"
                sql_names = cursor_name.execute(sql_names)
                print "./wa.db Database connected"

                try:
                    for data in sql_names:
                        names_dict.update({data[0]: data[1]})
                except Exception as e:
                    print "Error adding items in the dictionary:", e
        except Exception as e:
            print "Error connecting to Database, ", e
    else:
        print "wa database doesn't exist"


def gets_name(obj):
    """ Function recover a name of the wa.db"""
    if names_dict == {}:  # No exists wa.db
        return ""
    else:  # Exists Wa.db
        if type(obj) is list:  # It's a list
            list_broadcast = []
            for i in obj:
                b = i + "@s.whatsapp.net"
                if b in names_dict:
                    if names_dict[b] is not None:
                        list_broadcast.append(names_dict[b])
                    else:
                        list_broadcast.append(i)
                else:
                    list_broadcast.append(i)
            return "(" + ", ".join(list_broadcast) + ")"
        else:  # It's a string
            if obj in names_dict:
                if names_dict[obj] is not None:
                    return "(" + names_dict[obj] + ")"
                else:
                    return ""
            else:
                return ""


def report(obj, html):
    """ Function that makes the report """
    rep_ini = ""
    if report_var == 'EN':
        rep_ini = """
        <!DOCTYPE html>
        <html lang='""" + report_var + """'>
    
        <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Report makes with Whatsapp Parser Tool">
        <meta name="author" content="B16f00t">
        <link rel="shortcut icon" href="../cfg/logo.png">
        <title>Whatsapp Parser Tool v""" + version + """ Report</title>
        <!-- Bootstrap core CSS -->
        <link href="dist/css/bootstrap.css" rel="stylesheet">
        <!-- Bootstrap theme -->
        <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
        <!-- Custom styles for this template -->
        <link href="../cfg/chat.css" rel="stylesheet">
        </head>
    
        <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        tr:nth-child(even) {
        background-color: #dddddd;
        }
        #map {
            height: 100px;
            width: 100%;
        }
        </style>
        
        <body>
        <!-- Fixed navbar -->
          <div class="container theme-showcase">
            <div class="header">
            <table style="width:100%">
            <caption><img src=../""" + logo + """ height=128 width=128 align="left"><h1>&nbsp&nbsp&nbsp&nbsp""" + company + """</h1></caption>
            <tr>
                <th>Record</th>
                <th>Unit / Company</th> 
                <th>Examiner</th>
                <th>Date</th>
            </tr>
            <tr>
                <td>""" + record + """</td>
                <td>""" + unit + """</td>
                <td>""" + examiner + """</td>
                <td>""" + time.strftime('%d-%m-%Y', time.localtime()) + """</td>
            </tr>
            <tr>
                <th colspan="4">Notes</th>
            </tr>
            <tr>
                <td colspan="4">""" + notes + """</td>
            </tr>
            </table>
            <h2 align=center> Chat </h2>
            <h3 align=center> """ + arg_group + " " + gets_name(arg_group) + arg_user + " " + gets_name(arg_user + "@s.whatsapp.net") + """ </h3>
            </div>
          <div class="container">
            <ul>
        """
    elif report_var == 'ES':
        rep_ini = """
        <!DOCTYPE html>
        <html lang='""" + report_var + """'>
        
        <head>
        <meta charset="utf-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="description" content="Informe creado por WhatsApp Parser Tool">
        <meta name="author" content="B16f00t">
        <link rel="shortcut icon" href="../cfg/logo.png">
        <title>Whatsapp Parser Tool v0.3 Report</title>
        <!-- Bootstrap core CSS -->
        <link href="dist/css/bootstrap.css" rel="stylesheet">
        <!-- Bootstrap theme -->
        <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
        <!-- Custom styles for this template -->
        <link href="../cfg/chat.css" rel="stylesheet">
        </head>

        <style>
        table {
        font-family: arial, sans-serif;
        border-collapse: collapse;
        width: 100%;
        }
        td, th {
        border: 1px solid #dddddd;
        text-align: left;
        padding: 8px;
        }
        tr:nth-child(even) {
        background-color: #dddddd;
        }
        #map {
            height: 100px;
            width: 100%;
        }
        </style>

        <body>
        <!-- Fixed navbar -->
          <div class="container theme-showcase">
            <div class="header">
            <table style="width:100%">
            <caption><img src=../""".decode('utf-8') + logo + """ height=128 width=128 align="left"><h1>&nbsp&nbsp&nbsp&nbsp""" + company + """</h1></caption>
            <tr>
                <th>Registro</th>
                <th>Unidad / Compañia</th> 
                <th>Examinador</th>
                <th>Fecha</th>
            </tr>
            <tr>
                <td>""".decode('utf-8') + record + """</td>
                <td>""" + unit + """</td>
                <td>""" + examiner + """</td>
                <td>""" + time.strftime('%d-%m-%Y', time.localtime()) + """</td>
            </tr>
            <tr>
                <th colspan="4">Observaciones</th>
            </tr>
            <tr>
                <td colspan="4">""" + notes + """</td>
            </tr>
            </table>
            <h2 align=center> Conversación </h2>
            <h3 align=center> """.decode('utf-8') + arg_group + " " + gets_name(arg_group) + arg_user + " " + gets_name(arg_user + "@s.whatsapp.net") + """ </h3>
            </div>
          <div class="container">
            <ul>
        """

    rep_end = """
        </ul>
    </div>
    <!-- /container -->
    <!-- Bootstrap core JavaScript
        ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="dist/js/bootstrap.min.js"></script>
    <script src="docs-assets/js/holder.js"></script>
    </body>
    </html>
    """
    if os.path.isfile("./reports") is False:
        distutils.dir_util.mkpath("./reports")

    f = open(html, 'w')
    f.write(rep_ini.encode("UTF-8") + obj.encode("UTF-8") + rep_end.encode("UTF-8"))
    f.close()


def index_report(obj, html):
    """ Function that makes the index report """
    rep_ini = """
    <!DOCTYPE html>
    <html lang='""" + report_var + """'>

    <head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Report makes with Whatsapp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="../cfg/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report Index</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="../cfg/chat.css" rel="stylesheet">
    </head>

    <style>
    table {
    font-family: arial, sans-serif;
    border-collapse: collapse;
    width: 100%;
    }
    td, th {
    border: 1px solid #dddddd;
    text-align: left;
    padding: 8px;
    }
    tr:nth-child(even) {
    background-color: #dddddd;
    }
    #map {
        height: 100px;
        width: 100%;
    }
    </style>

    <body>
    <!-- Fixed navbar -->
      <div class="container theme-showcase">
      <caption><img src=../""" + logo + """ height=128 width=128 align="left"><h1>&nbsp&nbsp&nbsp&nbsp""" + company + """</h1></caption>
      <h2 align=center> Whatsapp Messaging Content </h2>

        <div class="header">
        <table style="width:100%"">
        """ + obj + """
        </table>
        </div>
      <div class="container">
        <ul>
        </ul>
    </div>
    <!-- /container -->
    <!-- Bootstrap core JavaScript
        ================================================== -->
    <!-- Placed at the end of the document so the pages load faster -->
    <script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
    <script src="dist/js/bootstrap.min.js"></script>
    <script src="docs-assets/js/holder.js"></script>
    </body>
    </html>
    """
    if os.path.isfile("./reports") is False:
        distutils.dir_util.mkpath("./reports")

    f = open(html, 'w')
    f.write(rep_ini.encode("UTF-8"))
    f.close()


def create_settings_file():
    """ Function that creates the settings file """
    with open('./cfg/settings.cfg', 'w') as cfg:
        cfg.write('[report]\nlogo = ./cfg/logo.png\ncompany =\nrecord =\nunit =\nexaminer =\nnotes =\n\n[auth]\ngmail = alias@gmail.com\npassw = yourpassword\ndevid = 1234567887654321\ncelnumbr = BackupPhoneNunmber\n\n[app]\npkg = com.whatsapp\nsig = 38a0f7d505fe18fec64fbf343ecaaaf310dbd799\n\n[client]\npkg = com.google.android.gms\nsig = 38918a453d07199354f8b19af05ec6562ced5788\nver = 9877000')


def messages(consult, sql):
    """ Function that show database messages """
    try:
        n = 0
        rep_med = ""  # Saves the complete chat
        for data in consult:
            try:
                report_msj = ""  # Saves each message
                report_name = ""  # Saves the chat sender
                if int(data[8]) != -1:   # media_wa_type -1 "Start DB"
                    print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                    if int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "g.us":
                        if int(data[3]) == 6:  # Group system message
                            print Fore.GREEN + "From" + Fore.RESET,  data[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET
                            if report_var == 'EN':
                                report_name = "System Message"
                            elif report_var == 'ES':
                                report_name = "Mensaje de Sistema"

                        else:  # I send message to group
                            print Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to" + Fore.RESET, data[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET
                            if report_var == 'EN':
                                report_name = "Me"
                            elif report_var == 'ES':
                                report_name = "Yo"

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":  # I send message to somebody
                        if int(data[3]) == 6:  # sender system message
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET
                            if report_var == 'EN':
                                report_name = "System Message"
                            elif report_var == 'ES':
                                report_name = "Mensaje de Sistema"
                        else:  # I send a message to somebody
                            print Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET
                            if report_var == 'EN':
                                report_name = "Me"
                            elif report_var == 'ES':
                                report_name = "Yo"

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "broadcast":  # I send broadcast
                        if int(data[3]) == 6:  # broadcast system message
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET
                            if report_var == 'EN':
                                report_name = "System Message"
                            elif report_var == 'ES':
                                report_name = "Mensaje de Sistema"
                        else:  # I send to somebody by broadcast
                            list_broadcast = (str(data[15])).split('@')
                            list_copy = []
                            for i in list_broadcast:
                                list_copy.append("".join([x for x in i if x.isdigit()]))
                            list_copy.pop()
                            print Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to" + Fore.RESET, ", ".join(list_copy), Fore.YELLOW + gets_name(list_copy) + Fore.RESET, Fore.GREEN + "by broadcast" + Fore.RESET
                            if report_var == 'EN':
                                report_name = "&#128227; Me"
                            elif report_var == 'ES':
                                report_name = "&#128227; Yo"

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "g.us":  # Group send me a message
                        print Fore.GREEN + "From" + Fore.RESET, data[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET + Fore.GREEN + ", participant" + Fore.RESET, (str(data[15]).split('@'))[0], Fore.YELLOW + gets_name(data[15]) + Fore.RESET
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_name = (str(data[15]).split('@'))[0] + " " + gets_name(data[15])

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":
                        if data[15]:  # Somebody sends me a message by broadcast
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET, Fore.GREEN + "to" + Fore.RESET + " Me" + Fore.GREEN + " by broadcast" + Fore.RESET
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_name = "&#128227;" + (str(data[0]).split('@'))[0] + " " + gets_name(data[0])
                        else:  # Somebody sends me a message
                            if int(data[8]) == 10:
                                print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET  # sender system message
                                if report_var == 'EN':
                                    report_name = "System Message"
                                elif report_var == 'ES':
                                    report_name = "Mensaje de Sistema"
                            else:
                                print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.YELLOW + gets_name(data[0]) + Fore.RESET, Fore.GREEN + "to" + Fore.RESET + " Me"
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_name = (str(data[0]).split('@'))[0] + " " + gets_name(data[0])

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "broadcast":  # Somebody posts a Status
                        if os.path.isfile("./Media/.Statuses") is False:
                            distutils.dir_util.mkpath("./Media/.Statuses")
                        if int(data[1]) == 0:
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[15]).split('@'))[0], Fore.YELLOW + gets_name(data[15]) + Fore.RESET, Fore.GREEN + "posts status" + Fore.RESET
                        else:
                            print Fore.GREEN + "From" + Fore.RESET, "Me"

                        if report_var == 'EN':
                            if int(data[1]) == 0:
                                report_name = "Posts Status - " + (str(data[15]).split('@'))[0] + " " + gets_name(data[15])
                            else:
                                report_name = "I Post Status"
                        elif report_var == 'ES':
                            if int(data[1]) == 0:
                                report_name = "Publica Estado - " + (str(data[15]).split('@'))[0] + " " + gets_name(data[15])
                            else:
                                report_name = "Publico Estado"

                    if data[21] or int(data[21]) > 0:
                        cursor_record = str(data[23])
                        print Fore.RED + "Replying to:" + Fore.RESET, reply(data[21])[0]
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj = "<p style=\"border-left: 6px solid blue; background-color: lightgrey;border-radius:5px;\"; > " + reply(data[21])[1] + "</p>"
                        consult = cursor.execute(sql + " AND messages._id >= " + cursor_record)
                        consult = cursor.fetchone()
                    if int(data[8]) == 0:  # media_wa_type 0, text message
                        if int(data[3]) == 6:  # Status 6, system message
                            if int(data[9]) == 1:  # if media_size value change
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed the subject from '", str(data[17])[7:].decode('utf-8', 'ignore'), "' to '", data[4], "'"
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " changed the subject from ' " + cgi.escape(str(data[17][7:]).decode('utf-8')) + "' to '" + cgi.escape(data[4]) + "'"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " cambió el asunto de ' ".decode('utf-8') + cgi.escape(str(data[17][7:]).decode('utf-8')) + "' a '" + cgi.escape(data[4]) + "'"

                            elif int(data[9]) == 4:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "was added to the group"
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " was added to the group"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " fue añadido al grupo".decode('utf-8')

                            elif int(data[9]) == 5:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " +  gets_name(data[15]) + Fore.RESET, "left the group"
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " left the group"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " dejó el grupo".decode('utf-8')

                            elif int(data[9]) == 6:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed the group icon"
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " changed the group icon"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + " " + gets_name(data[15]) + " cambió el icono del grupo".decode('utf-8')
                                print "The last picture is stored on the phone path '/data/data/com.whatsapp/cache/Profile Pictures/" + (data[0].split('@'))[0] + ".jpg'"
                                if data[17]:
                                    if os.path.isfile("./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg") is False:
                                        print "Thumbnail was saved on local path './Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                        if (report_var == 'EN') or (report_var == 'ES'):
                                            report_msj += "</br>./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                        distutils.dir_util.mkpath("./Media/profiles")
                                        with open("./cfg/buffer", 'wb') as buffer_copy:
                                            buffer_copy.write(str(data[17]))
                                        with open("./cfg/buffer", 'rb') as buffer_copy:
                                            i = 0
                                            while True:
                                                x = buffer_copy.read(1)
                                                x = hex(ord(x))
                                                if x == "0xd8":
                                                    break
                                                else:
                                                    i += 1
                                            buffer_copy.seek(0, 0)
                                            buffer_copy.seek(i - 1)
                                            new_file = buffer_copy.read()
                                            file_created = "./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg"
                                            with open(file_created, 'wb') as profile_file:
                                                profile_file.write(new_file)
                                    else:
                                        print "Thumbnail stored on local path './Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += "<br> <a href=\"../Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg\" target=\"_blank\"> <IMG SRC=\"../Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg\" width=\"100\" height=\"100\"/></a>"

                            elif int(data[9]) == 7:
                                print Fore.GREEN + "Message:" + Fore.RESET + " Removed", data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "from the list"
                                if report_var == 'EN':
                                    report_msj += " Removed " + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " from the list"
                                elif report_var == 'ES':
                                    report_msj += " Removío ".decode('utf-8') + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " de la lista"

                            elif int(data[9]) == 9:
                                list_broadcast = (str(data[17])).split('@')
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append("".join([x for x in i if x.isdigit()]))
                                list_copy.pop()
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "created a broadcast list with", ", ".join(list_copy), Fore.YELLOW + gets_name(list_copy) + Fore.RESET, "recipients"
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " created a broadcast list with " + ", ".join(list_copy) + gets_name(list_copy) + " recipients"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " creó una lista de difusión con ".decode('utf-8') + ", ".join(list_copy) + gets_name(list_copy) + " destinatarios"

                            elif int(data[9]) == 10:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed to", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + Fore.YELLOW + gets_name(((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " changed to " + ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + gets_name(((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net")
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " cambió a ".decode('utf-8') + ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + gets_name(((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net")

                            elif int(data[9]) == 11:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "created the group '", data[4], "'"
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " created the group ' " + cgi.escape(data[4]) + " '"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " creó el grupo ' ".decode('utf-8') + cgi.escape(data[4]) + " '"

                            elif int(data[9]) == 12:
                                if data[15]:  # whether exists remote_resource
                                    print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "added", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + Fore.YELLOW + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "to the group"
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " added " + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " to the group"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " añadió ".decode('utf-8') + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " al grupo"
                                else:
                                    print Fore.GREEN + "Message:" + Fore.RESET, "Added", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + Fore.YELLOW + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "to the group"
                                    if report_var == 'EN':
                                        report_msj += "Added " + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " to the group"
                                    elif report_var == 'ES':
                                        report_msj += "Se añadió ".decode('utf-8') + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " al grupo"
                            elif int(data[9]) == 14:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + " " + gets_name(data[15]) + Fore.RESET, "eliminated", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + Fore.YELLOW + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "from the group"
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " eliminated " + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " from the group"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " eliminó ".decode('utf-8') + ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " del grupo"

                            elif int(data[9]) == 15:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "made you administrator"
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " made you administrator"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " te hizo administrador"

                            elif int(data[9]) == 18:
                                if data[15]:
                                    print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed"
                                    if report_var == 'EN':
                                        report_msj += "The security code of " + data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " changed"
                                    elif report_var == 'ES':
                                        report_msj += "El código de seguridad de ".decode('utf-8') + data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " cambió".decode('utf-8')
                                else:
                                    print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[0].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[0]) + Fore.RESET, "changed"
                                    if report_var == 'EN':
                                        report_msj += "The security code of " + data[0].strip("@s.whatsapp.net") + " " + gets_name(data[0]) + " changed"
                                    elif report_var == 'ES':
                                        report_msj += "El código de seguridad de ".decode('utf-8') + data[0].strip("@s.whatsapp.net") + " " + gets_name(data[0]) + " cambió".decode('utf-8')

                            elif int(data[9]) == 19:
                                print Fore.GREEN + "Message:" + Fore.RESET + " Messages and calls in this chat are now protected with end-to-end encryption"
                                if report_var == 'EN':
                                    report_msj += "Messages and calls in this chat are now protected with end-to-end encryption"
                                elif report_var == 'ES':
                                    report_msj += "Los mensajes y llamadas en este chat ahora están protegidos con cifrado de extremo a extremo".decode('utf-8')

                            elif int(data[9]) == 20:
                                print Fore.GREEN + "Message:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + Fore.YELLOW + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "joined using an invitation link from this group"
                                if report_var == 'EN':
                                    report_msj += ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " joined using an invitation link from this group"
                                elif report_var == 'ES':
                                    report_msj += ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + " " + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + " se unió usando un enlace de invitación de este grupo".decode('utf-8')

                            elif int(data[9]) == 22:
                                print Fore.GREEN + "Message:" + Fore.RESET + " This chat could be with a company account"
                                if report_var == 'EN':
                                    report_msj += "This chat could be with a company account"
                                elif report_var == 'ES':
                                    report_msj += "Este chat podría ser con una cuenta de empresa".decode('utf-8')

                            elif int(data[9]) == 27:
                                if data[4] != "":
                                    print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed the group description to '" + data[4] + "'"
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " changed the group description to ' " + cgi.escape(data[4]) + " '"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " cambió la descripción del grupo a ' ".decode('utf-8') + cgi.escape(data[4]) + " '"
                                else:
                                    print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "deleted the group description"
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " deleted the group description"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + " " + gets_name(data[15]) + " borró la descripción del grupo".decode('utf-8')

                        else:
                            print Fore.GREEN + "Message:" + Fore.RESET, data[4]
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += cgi.escape(data[4])

                    elif int(data[8]) == 1:  # media_wa_type 1, Image
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "./" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8') + " - " + cgi.escape(data[11])
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8')
                        print Fore.GREEN + "Type: " + Fore.RESET + "image/jpeg" + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " " + size_file(int(data[9]))
                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Images/Sent")
                            if thumb == "Not downloaded":
                                epoch = time.strftime("%Y%m%d", time.localtime((int(data[5]) / 1000)))
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Images/Sent/IMG-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.jpg"
                                else:
                                    thumb = "./Media/WhatsApp Images/IMG-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.jpg"
                            print "Thumbnail was saved on local path '" + thumb + "'"
                            file_created = thumb
                            with open(file_created, 'wb') as profile_file:
                                if data[19]:  # raw_data exists
                                    profile_file.write(str(data[19]))
                                else:  # Gets the thumbnail of the message_thumbnails
                                    profile_file.write(str(data[22]))

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 2:  # media_wa_type 2, Audio
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Audio doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "./" + (str(data[17]))[i:b]
                        print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        print Fore.GREEN + "Type:" + Fore.RESET, data[7], Fore.GREEN + "- Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br>" + thumb.decode('utf-8') + " " + size_file(int(data[9])) + " - " + duration_file(data[12]) + "<br></br><audio controls> <source src=\"." + thumb.decode('utf-8') + "\" type=\"" + data[7] + "\"</audio>"

                    elif int(data[8]) == 3:  # media_wa_type 3 Video
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Video doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "./" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8') + " - " + cgi.escape(data[11])
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8')
                        print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " " + size_file(int(data[9])) + " - " + duration_file(data[12])
                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Video/Sent")
                            if thumb == "Not downloaded":
                                epoch = time.strftime("%Y%m%d", time.localtime((int(data[5]) / 1000)))
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Video/Sent/VID-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.mp4"
                                else:
                                    thumb = "./Media/WhatsApp Video/VID-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.mp4"
                            print "Thumbnail was saved on local path '" + thumb + "'"
                            file_created = thumb
                            with open(file_created, 'wb') as profile_file:
                                if data[19]:
                                    profile_file.write(str(data[19]))
                                else:
                                    profile_file.write(str(data[22]))

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br/> <a href=\"." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 4:  # media_wa_type 4, Contact
                        print Fore.GREEN + "Name:" + Fore.RESET, data[10], Fore.GREEN + "- Type:" + Fore.RESET + " Contact vCard"
                        if report_var == 'EN':
                            report_msj += cgi.escape(data[10]) + " &#9742;  Contact vCard"
                        elif report_var == 'ES':
                            report_msj += cgi.escape(data[10]) + " &#9742;  Contacto vCard"

                    elif int(data[8]) == 5:  # media_wa_type 5, Location
                        if data[6]:  # media_url exists
                            if data[10]:  # media_name exists
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6], Fore.GREEN + "- Name:" + Fore.RESET, data[10]
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += cgi.escape(data[6]) + " - " + cgi.escape(data[10])
                            else:
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6]
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += cgi.escape(data[6])
                        else:
                            if data[10]:
                                print Fore.GREEN + "Name:" + Fore.RESET, data[10]
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += cgi.escape(data[10])
                        print Fore.GREEN + "Type:" + Fore.RESET + " Location" + Fore.GREEN + " - Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14]
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "(" + str(data[13]) + "," + str(data[14]) + ")" + "<br><a href=\"https://www.google.es/maps/search/(" + str(data[13]) + "," + str(data[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(data[13]) + "," + str(data[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(data[13]) + "," + str(data[14]) + "&sensor=false\"/></a>"

                    elif int(data[8]) == 8:  # media_wa_type 8, Audio / Video Call
                        print Fore.GREEN + "Call:" + Fore.RESET, str(data[11]).capitalize(), Fore.GREEN + "- Duration:" + Fore.RESET, duration_file(data[12])
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "&#128222; " + str(data[11]).capitalize() + " " + duration_file(data[12])

                    elif int(data[8]) == 9:  # media_wa_type 9, Application
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "./" + chain[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8') + " - " + cgi.escape(data[11])
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8')
                        if int(data[12]) > 0:
                            print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Pages:" + Fore.RESET, data[12]
                            if report_var == 'EN':
                                report_msj += " " + size_file(int(data[9])) + " - " + str(data[12]) + " Pages"
                            elif report_var == 'ES':
                                report_msj += " " + size_file(int(data[9])) + " - " + str(data[12]) + " Páginas".decode('utf-8')
                        else:
                            print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += " " + size_file(int(data[9]))
                        if os.path.isfile(thumb + ".jpg") is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Documents/Sent")
                            if thumb == "Not downloaded":
                                epoch = time.strftime("%Y%m%d", time.localtime((int(data[5]) / 1000)))
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Documents/Sent/DOC-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded"
                                else:
                                    thumb = "./Media/WhatsApp Documents/DOC-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded"
                            print "Thumbnail was saved on local path '" + thumb + ".jpg'"
                            file_created = thumb + ".jpg"
                            with open(file_created, 'wb') as profile_file:
                                if data[19]:
                                    profile_file.write(str(data[19]))
                                else:
                                    profile_file.write(str(data[22]))
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='." + thumb.decode('utf-8') + ".jpg' width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 10:  # media_wa_type 10, Video/Audio call lost
                        print Fore.GREEN + "Message:" + Fore.RESET, "Missed " + str(data[11]).capitalize() + " call"
                        if report_var == 'EN':
                            report_msj += "&#128222; Missed" + str(data[11]).capitalize() + " call"
                        elif report_var == 'ES':
                            report_msj += "&#128222; " + str(data[11]).capitalize() + " llamada perdida"

                    elif int(data[8]) == 11:  # media_wa_type 11, Waiting for message
                        print Fore.GREEN + "Message:" + Fore.RESET, "Waiting for message. This may take tiMe"
                        if report_var == 'EN':
                            report_msj += "<p style=\"color:#FF0000\";>&#9842; Waiting for message. This may take time </p>"
                        elif report_var == 'ES':
                            report_msj += "<p style=\"color:#FF0000\";>&#9842; Esperando mensaje. Esto puede tomar tiempo</p>"

                    elif int(data[8]) == 13:  # media_wa_type 13 Gif
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Video doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "./" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8') + " - " + cgi.escape(data[11])
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb.decode('utf-8')
                        print Fore.GREEN + "Type: " + Fore.RESET + "Gif" + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " - Gif - " + size_file(int(data[9])) + " " + duration_file(data[12])
                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Animated Gifs/Sent")
                            epoch = time.strftime("%Y%m%d", time.localtime((int(data[5]) / 1000)))
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Animated Gifs/Sent/VID-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.mp4"
                                else:
                                    thumb = "./Media/WhatsApp Animated Gifs/VID-" + epoch + "-" + str(int(data[5]) / 1000) + "-NotDownloaded.mp4"
                            print "Thumbnail was saved on local path '" + thumb + "'"
                            file_created = thumb
                            with open(file_created, 'wb') as profile_file:
                                if data[19]:
                                    profile_file.write(str(data[19]))
                                else:
                                    profile_file.write(str(data[22]))

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb.decode('utf-8') + "\" target=\"_blank\"> <IMG SRC='." + thumb.decode('utf-8') + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 15:  # media_wa_type 15, Deleted Object
                        if int(data[16]) == 5:  # edit_version 5, deleted for me
                            print Fore.GREEN + "Message:" + Fore.RESET + " Message deleted for Me"
                            if report_var == 'EN':
                                report_msj += "Message deleted for Me"
                            elif report_var == 'ES':
                                report_msj += "Mensaje eliminado para mí".decode('utf-8')
                        elif int(data[16]) == 7:  # edit_version 7, deleted for all
                            print Fore.GREEN + "Message:" + Fore.RESET + " Message deleted for all participants"
                            if report_var == 'EN':
                                report_msj += "Message deleted for all participants"
                            elif report_var == 'ES':
                                report_msj += "Mensaje eliminado para todos los destinatarios"

                    elif int(data[8]) == 16:  # media_wa_type 16, Share location
                        print Fore.GREEN + "Type:" + Fore.RESET + " Real time location " + Fore.GREEN + "- Caption:" + Fore.RESET, data[11], Fore.GREEN + "- Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14], Fore.GREEN + "- Duration:" + Fore.RESET, duration_file(data[12])
                        if report_var == 'EN':
                            report_msj += "Real time location (" + str(data[13]) + "," + str(data[14]) + ") - " + '' if data[11] is None else cgi.escape(data[11])
                            report_msj += " <br><a href=\"https://www.google.es/maps/search/(" + str(data[13]) + "," + str(data[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(data[13]) + "," + str(data[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(data[13]) + "," + str(data[14]) + "&sensor=false\"/></a>"
                        elif report_var == 'ES':
                            report_msj += "Ubicación en tiempo real (".decode('utf-8') + str(data[13]) + "," + str(data[14]) + ") - " + cgi.escape(data[11])
                            report_msj += " <br><a href=\"https://www.google.es/maps/search/(" + str(data[13]) + "," + str(data[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(data[13]) + "," + str(data[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(data[13]) + "," + str(data[14]) + "&sensor=false\"/></a>"

                    if data[20]:
                        if int(data[20]) == 1:
                            print Fore.YELLOW + "Starred message" + Fore.RESET
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += "<br> &#127775; "
                    main_status, report_status = status(int(data[3]))
                    print Fore.GREEN + "Timestamp:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000)), Fore.GREEN + "- Status:" + Fore.RESET, main_status
                    if report_var == 'EN':
                        report_time = time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))
                        if (report_name == "Me") or (report_name == "&#128227; Me"):
                            rep_med += """
                            <li>
                            <div class="bubble"> <span class="personName">""" + report_name + """</span> <br>
                                <span class="personSay">""" + report_msj + """</span> </div>
                            <span class=" time round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
                        else:
                            rep_med += """
                            <li>
                            <div class="bubble2"> <span class="personName2">""" + report_name + """</span> <br>
                                <span class="personSay2">""" + report_msj + """</span> </div>
                            <span class=" time2 round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
                    elif report_var == 'ES':
                        report_time = time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))
                        if (report_name == "Yo") or (report_name == "&#128227; Yo"):
                            rep_med += """
                            <li>
                            <div class="bubble"> <span class="personName">""" + report_name + """</span> <br>
                                <span class="personSay">""" + report_msj + """</span> </div>
                            <span class=" time round ">""" + report_time.decode('utf-8') + "&nbsp" + report_status.decode('utf-8') + """</span> </li>"""
                        else:
                            rep_med += """
                            <li>
                            <div class="bubble2"> <span class="personName2">""" + report_name + """</span> <br>
                                <span class="personSay2">""" + report_msj + """</span> </div>
                            <span class=" time2 round ">""" + report_time.decode('utf-8') + "&nbsp" + report_status.decode('utf-8') + """</span> </li>"""

                n += 1

            except Exception as e:
                print "Error showing message details:", e
                continue
        if report_var:
            global report_html
            if not args.all:
                report_html = "./reports/report.html"
                if args.user:
                    report_html = "./reports/report_user_chat_" + args.user + "_" + gets_name(args.user + "@s.whatsapp.net") + ".html"
                if args.group:
                    report_html = "./reports/report_group_chat_" + args.group + "_" + gets_name(args.group) + ".html"
            report(rep_med, report_html)

    except Exception as e:
        print "An error occurred connecting to the database", e


def info(consult):
    """ Function that show info """
    info_dic = {}  # i:[Key_Remote_jid, data, type]
    i = 2
    try:
        for data in consult:
            try:
                if int(data[3]) == 6:  # Status 6, control message
                    if int(data[9]) == 11:  # media size 11 --> Group
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'group']})
                    elif int(data[9]) == 9:  # media size 9 --> Broadcast
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'broadcast']})

            except Exception as e:
                print "Error adding items in the dictionary:", e
                continue

        for dic_key, dic_value in info_dic.items():  # A group create with the last name
            sql_key = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                      remote_resource FROM messages WHERE (key_remote_jid = '" + dic_value[0] + "' and status = 6 and media_size = 1);"
            consult_key = cursor.execute(sql_key)
            for data in consult_key:
                if data[4]:
                    info_dic.update({dic_key: [data[0], data[4], 'group']})

    except Exception as e:
        print "An error occurred connecting to the database", e

    while True:
        print "\n-------------------------- INFO MODE ----------------------------"
        print "0  ) Exit"
        print "1  ) Statuses"
        print "2  ) Chat list"
        for key, value in info_dic.items():
            i = key
            if key < 10:
                if value[2] == "group":
                    print key, " )", value[0], "-", value[1]
                else:
                    print key, " )", value[0], "-", value[2]
            else:
                if value[2] == "group":
                    print key, ")", value[0], "-", value[1]
                else:
                    print key, ")", value[0], "-", value[2]
        print "------------------------------------------------------------------"
        try:
            opt = int(input("\nChoose a number option: "))
            if opt == 0:
                break
            elif opt == 1:
                sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                             remote_resource, edit_version,thumb_image, recipient_count, raw_data FROM messages WHERE key_remote_jid = 'status@broadcast';"
                consult = cursor.execute(sql_string)
                print "\n\n\t*** Statuses ***\n"
                for data in consult:
                    try:
                        print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                        if data[17]:  # thumb_image
                            if int(data[1]) == 0:
                                print Fore.GREEN + "From" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET
                            else:
                                print Fore.GREEN + "From" + Fore.RESET, "Me"

                            chain = str(data[17]).split('w')[0]
                            i = chain.rfind("Media/")
                            b = len(chain)
                            if i == -1:  # Image doesn't exist
                                thumb = "Not displayed"
                            else:
                                thumb = "/" + (str(data[17]))[i:b]
                            if data[11]:  # media_caption
                                print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            else:
                                print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if int(data[12]) > 0:
                                print Fore.GREEN + "Type: " + Fore.RESET + str(data[7]) + Fore.GREEN + " - Size:" + Fore.RESET, str(data[9]), "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                            else:
                                print Fore.GREEN + "Type: " + Fore.RESET + str(data[7]) + Fore.GREEN + " - Size:" + Fore.RESET, str(data[9]), "bytes " + size_file(int(data[9]))
                            if thumb != "Not displayed":
                                print "The picture is stored on the phone path '" + thumb + "'"
                            print Fore.GREEN + "Timestamp:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000)), Fore.GREEN + "- Status:" + Fore.RESET, status(int(data[3]))[0]
                    except Exception as e:
                        print "Status error", e
                        continue
            elif opt == 2:
                sql_consult_info = cursor.execute("SELECT key_remote_jid, subject FROM chat_list;")
                info_number = {}
                print
                for data in sql_consult_info:
                    info_number.update({data[0]: data[1]})
                for key, value in info_number.items():
                    if key.split('@')[1] == "g.us":
                        print Fore.RED + key + Fore.RESET, Fore.YELLOW + (value if value else gets_name(key)) + Fore.RESET
                    elif key.split('@')[1] == "s.whatsapp.net":
                        print Fore.GREEN + key.split('@')[0] + Fore.RESET, Fore.YELLOW + gets_name(key) + Fore.RESET
                    elif key.split('@')[1] == "broadcast" and i != "status@broadcast":
                        print Fore.BLUE + key + Fore.RESET

            elif opt > i:
                print "Bad option"
            else:  # Select a valid option
                while True:
                    if info_dic[opt][1]:
                        print "\n\n\t***", info_dic[opt][1], "***\n"
                    else:
                        print "\n\n\t*** Broadcast ***\n"
                    print "0 ) Back"
                    print "1 ) Creator and creation timestamp"
                    print "2 ) Participants"
                    print "3 ) Log\n"
                    try:
                        opt2 = int(input("Choose a number option: "))
                        if opt2 == 0:
                            break

                        elif opt2 == 1:
                            if info_dic[opt][1]:  # if it's a group
                                a = info_dic[opt][0].split("-")
                                b = a[1].split("@")
                                print "\n    Creator User          Timestamp               NaMe"
                                print "---------------------------------------------------------------------------"
                                print "   ", a[0], "\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(b[0]))), "\t", Fore.YELLOW + gets_name(a[0] + "@s.whatsapp.net") + Fore.RESET
                            else:  # if it's a broadcast
                                a, b = info_dic[opt][0].split("@")
                                print "\n    Creator User          Timestamp"
                                print "--------------------------------------------"
                                print "       Me \t\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(a)))

                        elif opt2 == 2:
                            sql_string_info = "SELECT gjid, jid, admin, pending, sent_sender_key FROM group_participants WHERE gjid = '" + info_dic[opt][0] + "';"
                            consult_info = cursor.execute(sql_string_info)
                            i = 0
                            if info_dic[opt][1]:  # if it's a group
                                print "\n     Phone User        Admin            NaMe"
                                print "-----------------------------------------------------------------"
                                for data in consult_info:
                                    if data[1]:
                                        i += 1
                                        if i > 9:
                                            print i, ")", data[1].strip("@s.whatsapp.net"), '\tYes' if int(data[2]) == 1 else '\tNo', "\t", Fore.YELLOW + gets_name(data[1]) + Fore.RESET
                                        else:
                                            print i, " )", data[1].strip("@s.whatsapp.net"), '\tYes' if int(data[2]) == 1 else '\tNo', "\t", Fore.YELLOW + gets_name(data[1]) + Fore.RESET
                                    else:
                                        i += 1
                                        print i, " ) Me\t\t\t", 'Yes' if int(data[2]) == 1 else 'No'
                            else:  # if it's a broadcast
                                print "\n     Phone User"
                                print "-----------------------------"
                                for data in consult_info:
                                    i += 1
                                    print i, ")", data[1].strip("@s.whatsapp.net")

                        elif opt2 == 3:
                            sql_string_info = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, \
                                              latitude, longitude, remote_resource, edit_version, thumb_image, recipient_count FROM messages WHERE key_remote_jid = '" + info_dic[opt][0] + "';"
                            consult_info = cursor.execute(sql_string_info)
                            try:
                                for data in consult_info:
                                    if (int(data[8]) == 0) and (int(data[3]) == 6):
                                        print Fore.RED + "---------------------------------------------------------------------" + Fore.RED

                                        if int(data[9]) == 1:  # if media_size value change
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "changed the subject from '", str(data[17])[7:].decode('utf-8', 'ignore'), "' to '", data[4], "'"
                                        elif int(data[9]) == 4:
                                            if info_dic[opt][1]:
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "was added to the group"
                                            else:
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "was added to the list"
                                        elif int(data[9]) == 5:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "left the group"
                                        elif int(data[9]) == 6:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "changed the group icon"
                                            if data[17]:
                                                print "The last picture is stored on the phone path '/data/data/com.whatsapp/cache/Profile Pictures/" + (data[0].split('@'))[0] + ".jpg'"
                                                print "Thumbnail was saved on local path '" + os.getcwd() + "/Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                            else:
                                                print "Thumbnail null"
                                            if not os.path.isdir("./Media/profiles"):
                                                os.mkdir("./Media/profiles")
                                            with open("./cfg/buffer", 'wb') as buffer_copy:
                                                buffer_copy.write(str(data[17]))
                                            with open("./cfg/buffer", 'rb') as buffer_copy:
                                                i = 0
                                                if data[17]:
                                                    while True:
                                                        x = buffer_copy.read(1)
                                                        x = hex(ord(x))
                                                        if x == "0xd8":
                                                            break
                                                        else:
                                                            i += 1
                                                    buffer_copy.seek(0, 0)
                                                    buffer_copy.seek(i-1)
                                                    new_file = buffer_copy.read()
                                                    file_created = "./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg"
                                                    with open(file_created, 'wb') as profile_file:
                                                        profile_file.write(new_file)

                                        elif int(data[9]) == 7:
                                            print Fore.GREEN + "Message:" + Fore.RESET + " Removed", data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "from the list"
                                        elif int(data[9]) == 9:
                                            list_broadcast = (str(data[17])).split('@')
                                            list_copy = []
                                            for i in list_broadcast:
                                                list_copy.append("".join([x for x in i if x.isdigit()]))
                                            list_copy.pop()
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "created a broadcast list with", ", ".join(list_copy), Fore.YELLOW + gets_name(list_copy) + Fore.RESET, "recipients"
                                        elif int(data[9]) == 10:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "changed to", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0], Fore.YELLOW + gets_name(((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET
                                        elif int(data[9]) == 11:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "created the group '", data[4], "'"
                                        elif int(data[9]) == 12:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "added", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], Fore.YELLOW + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "to the group"
                                        elif int(data[9]) == 14:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "eliminated", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], Fore.YELLOW + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "from the group"
                                        elif int(data[9]) == 15:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "made you administrator"
                                        elif int(data[9]) == 18:
                                            if data[15]:
                                                print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[15].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[15]) + Fore.RESET, "changed"
                                            else:
                                                print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[0].strip("@s.whatsapp.net"), Fore.YELLOW + gets_name(data[0]) + Fore.RESET, "changed"
                                        elif int(data[9]) == 19:
                                            print Fore.GREEN + "Message:" + Fore.RESET + " Messages and calls in this chat are now protected with end-to-end encryption"
                                        elif int(data[9]) == 20:
                                            print Fore.GREEN + "Message:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], Fore.YELLOW + gets_name(((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0] + "@s.whatsapp.net") + Fore.RESET, "joined using an invitation link from this group"
                                        elif int(data[9]) == 22:
                                            print Fore.GREEN + "Message:" + Fore.RESET + " This chat could be with a company account"
                                        elif int(data[9]) == 27:
                                            if data[4] != "":
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "changed the group description to ' " + data[4] + " '"
                                            else:
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net") + Fore.YELLOW + " " + gets_name(data[15]) + Fore.RESET, "deleted the group description"

                                        print Fore.GREEN + "Timestamp:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))

                            except Exception as e:
                                print "Error showing message details:", e
                                continue
                        else:
                            print "Bad option"

                    except Exception as e:
                        print "Error input data", e

        except Exception as e:
            print "Error input data", e


def get_configs():
    """ Function that gets report config"""
    global logo, company, record, unit, examiner, notes
    config_report = ConfigParser()
    try:
        config_report.read('./cfg/settings.cfg')
        logo = config_report.get('report', 'logo')
        company = config_report.get('report', 'company')
        record = config_report.get('report', 'record')
        unit = config_report.get('report', 'unit')
        examiner = config_report.get('report', 'examiner')
        notes = config_report.get('report', 'notes')
    except Exception as e:
        print "The 'settings.cfg' file is missing or corrupt!"


def extract(obj, total):
    """ Functions that extracts thumbnails"""
    i = 1
    for data in obj:
        try:
            chain = str(data[2]).split('w')[0]
            a = chain.rfind("Media/")
            if a == -1:  # Image doesn't exist
                thumb = "Not downloaded"
            else:
                a = chain.rfind("/")
                b = len(chain)
                thumb = "./thumbnails" + (str(data[2]))[a:b]

            if os.path.isfile(thumb) is False:
                distutils.dir_util.mkpath("./thumbnails")

            if thumb == "Not downloaded":
                epoch = time.strftime("%Y%m%d", time.localtime((int(data[4]) / 1000)))
                thumb = "./thumbnails/IMG-" + epoch + "-" + str(int(data[4]) / 1000) + "-NotDownloaded.jpg"
            if int(data[1]) == 9:
                thumb += ".jpg"

            file_created = thumb
            with open(file_created, 'wb') as profile_file:
                if data[3]:  # raw_data exists
                    profile_file.write(str(data[3]))
                else:  # Gets the thumbnail of the message_thumbnails
                    profile_file.write(str(data[5]))

            sys.stdout.write("\rExtracting thumbnail " + str(i) + " / " + str(total))
            sys.stdout.flush()
            i += 1
        except Exception as e:
            print "Error extracting:", e
    print "\n"
    print "Extraction Complete. Thumbnails save in './thumbnails' path"


#  Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="To start choose a database and a mode with options")
    parser.add_argument("database", help="Database file path - './msgstore.db' by default", metavar="DATABASE", nargs='?', default="./msgstore.db")
    mode_parser = parser.add_mutually_exclusive_group()
    mode_parser.add_argument("-k", "--key", help="*** Decrypt Mode *** - key file path")
    mode_parser.add_argument("-i", "--info", help="*** Info Mode ***", action="store_true")
    mode_parser.add_argument("-m", "--messages", help="*** Message Mode ***", action="store_true")
    mode_parser.add_argument("-e", "--extract", help="*** Extract Mode ***", action="store_true")
    parser.add_argument("--update", help='Update Whatsapp Parser Tool', action="store_true")
    user_parser = parser.add_mutually_exclusive_group()
    user_parser.add_argument("-u", "--user", help="Show chat with a phone number, ej. 34123456789")
    user_parser.add_argument("-ua", "--user_all", help="Show messages made by a phone number")
    user_parser.add_argument("-g", "--group", help="Show chat with a group number, ej. 34123456-14508@g.us")
    user_parser.add_argument("-a", "--all", help="Show all chat messages classified by phone number, group number and broadcast list", action="store_true")
    parser.add_argument("-t", "--text", help="Show messages by text match")
    parser.add_argument("-w", "--web", help="Show messages made by Whatsapp Web", action="store_true")
    parser.add_argument("-s", "--starred", help="Show messages starred by owner", action="store_true")
    parser.add_argument("-b", "--broadcast", help="Show messages send by broadcast", action="store_true")
    parser.add_argument("-ts", "--time_start", help="Show messages by start time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-te", "--time_end", help="Show messages by end time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-r", "--report", help='Make an html report in \'EN\' English or \'ES\' Spanish. If specified together with flag -a, makes a report for each chat', const='EN', nargs='?', choices=['EN', 'ES'])
    filter_parser = parser.add_mutually_exclusive_group()
    filter_parser.add_argument("-tt", "--type_text", help="Show text messages", action="store_true")
    filter_parser.add_argument("-ti", "--type_image", help="Show image messages", action="store_true")
    filter_parser.add_argument("-ta", "--type_audio", help="Show audio messages", action="store_true")
    filter_parser.add_argument("-tv", "--type_video", help="Show video messages", action="store_true")
    filter_parser.add_argument("-tc", "--type_contact", help="Show contact messages", action="store_true")
    filter_parser.add_argument("-tl", "--type_location", help="Show location messages", action="store_true")
    filter_parser.add_argument("-tx", "--type_call", help="Show audio/video call messages", action="store_true")
    filter_parser.add_argument("-tp", "--type_application", help="Show application messages", action="store_true")
    filter_parser.add_argument("-tg", "--type_gif", help="Show GIF messages", action="store_true")
    filter_parser.add_argument("-td", "--type_deleted", help="Show deleted object messages", action="store_true")
    filter_parser.add_argument("-tr", "--type_share", help="Show Real time location messages", action="store_true")
    args = parser.parse_args()
    init()
    if os.path.isfile('./cfg/settings.cfg') is False:
        create_settings_file()
    if len(sys.argv) == 1:
        help()
    else:
        if args.update:
            update = open("update.sh", "w")
            update.write("echo [i] Updating" + os.linesep)
            update.write("echo     [-] README.md" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/doc/requirements.txt -O ./doc/requirements.txt 2> /dev/null" + os.linesep)
            update.write("echo     [-] CHANGELOG.md" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/doc/CHANGELOG.md -O ./doc/CHANGELOG.md 2> /dev/null" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/whagdext.py 2> /dev/null" + os.linesep)
            update.write("echo     [-] requirements.txt" + os.linesep)
            update.write("echo     [-] settings.cfg" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/cfg/settings.cfg -O ./cfg/settings.cfg 2> /dev/null" + os.linesep)
            update.write("echo     [-] whapa.py" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/whapa.py 2> /dev/null" + os.linesep)
            update.write("echo     [-] whademe.py" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/whademe.py 2> /dev/null" + os.linesep)
            update.write("echo     [-] whagodri.py" + os.linesep)
            update.write("wget -N https://raw.githubusercontent.com/B16f00t/whapa/master/whagodri.py 2> /dev/null" + os.linesep)
            #update.write("python whapa.py")
            #update.write("python whademe.py")
            #update.write("python whagodri.py")
            update.write("rm update.sh" + os.linesep)
            update.close()
            os.system("sh update.sh")
        elif args.messages:
            names("wa.db")
            db_connect(args.database)
            sql_string = "SELECT messages.key_remote_jid, messages.key_from_me, messages.key_id, messages.status, messages.data, messages.timestamp, messages.media_url, messages.media_mime_type," \
                         " messages.media_wa_type, messages.media_size, messages.media_name, messages.media_caption, messages.media_duration, messages.latitude, messages.longitude, " \
                         " messages.remote_resource, messages.edit_version, messages.thumb_image, messages.recipient_count, messages.raw_data, messages.starred, messages.quoted_row_id, " \
                         " message_thumbnails.thumbnail, messages._id FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN '"
            try:
                epoch_start = "0"
                """ current date in Epoch milliseconds string """
                epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

                if args.time_start:
                    epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
                if args.time_end:
                    epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))
                sql_string = sql_string + str(epoch_start) + "' AND '" + str(epoch_end) + "'"

                if args.user:
                    sql_string = sql_string + " AND (messages.key_remote_jid LIKE '%" + str(args.user) + "%@s.whatsapp.net')"
                if args.user_all:
                    sql_string = sql_string + " AND (messages.key_remote_jid LIKE '%" + str(args.user_all) + "%@s.whatsapp.net' OR messages.remote_resource LIKE '%" + str(args.user_all) + "%')"
                    arg_user = args.user_all
                if args.group:
                    sql_string = sql_string + " AND messages.key_remote_jid LIKE '%" + str(args.group) + "%'"
                    arg_group = args.group
                if args.text:
                    sql_string = sql_string + " AND messages.data LIKE '%" + str(args.text) + "%'"
                if args.web:
                    sql_string = sql_string + " AND messages.key_id LIKE '3EB0%'"
                if args.starred:
                    sql_string = sql_string + " AND messages.starred = 1"
                if args.broadcast:
                    sql_string = sql_string + " AND messages.remote_resource LIKE '%broadcast%'"
                if args.report:
                    report_var = args.report
                    get_configs()
                if args.type_text:
                    sql_string = sql_string + " AND messages.media_wa_type = 0"
                if args.type_image:
                    sql_string = sql_string + " AND messages.media_wa_type = 1"
                if args.type_audio:
                    sql_string = sql_string + " AND messages.media_wa_type = 2"
                if args.type_video:
                    sql_string = sql_string + " AND messages.media_wa_type = 3"
                if args.type_contact:
                    sql_string = sql_string + " AND messages.media_wa_type = 4"
                if args.type_location:
                    sql_string = sql_string + " AND messages.media_wa_type = 5"
                if args.type_call:
                    sql_string = sql_string + " AND messages.media_wa_type = 8"
                if args.type_application:
                    sql_string = sql_string + " AND messages.media_wa_type = 9"
                if args.type_gif:
                    sql_string = sql_string + " AND messages.media_wa_type = 13"
                if args.type_deleted:
                    sql_string = sql_string + " AND messages.media_wa_type = 15"
                if args.type_share:
                    sql_string = sql_string + " AND messages.media_wa_type = 16"
                if args.all:
                    get_configs()
                    # Makes a set with with chats active by timestamp
                    chats_play = set()
                    sql_consult_chat = cursor.execute(sql_string + "AND messages.status != 6")
                    for data in sql_consult_chat:
                        chats_play.add(data[0])
                    chats_play.discard("-1"),
                    # Makes a dict with all chats with it subject
                    sql_consult_chat = cursor.execute("SELECT key_remote_jid, subject FROM chat_list;")
                    chats_total = {}
                    for data in sql_consult_chat:
                        chats_total.update({data[0]: data[1]})
                    # Makes a dict with actives chat by timestamp and it subject
                    chats = {}
                    for key, value in chats_total.items():
                        if key in chats_play:
                            chats.update({key: value})
                    sql_string_copy = sql_string
                    report_med = ""
                    for key, value in chats.items():
                        print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                        if key.split('@')[1] == "g.us":
                            print Fore.CYAN + "GROUP CHAT", key + Fore.RESET, Fore.YELLOW + "(" + value + ")" + Fore.RESET
                            report_html = "./reports/report_group_chat_" + key + "_" + "(" + value + ").html"
                            report_med += "<tr><th>Group</th><th><a href=\"report_group_chat_" + key + "_" + "(" + value + ").html" + "\" target=\"_blank\"> " + key + " " + "(" + value + ")</a></th></tr>"
                            arg_group = key
                            arg_user = ""
                        elif key.split('@')[1] == "s.whatsapp.net":
                            print Fore.CYAN + "USER CHAT", key + Fore.RESET, Fore.YELLOW + gets_name(key) + Fore.RESET
                            report_med += "<tr><th>User</th><th><a href=\"report_user_chat_" + key.split('@')[0] + "_" + gets_name(key) + ".html" + "\" target=\"_blank\"> " + key.split('@')[0] + " " + gets_name(key) + "</a></th></tr>"
                            report_html = "./reports/report_user_chat_" + key.split('@')[0] + "_" + gets_name(key) + ".html"
                            arg_group = ""
                            arg_user = key.split('@')[0]
                        elif key.split('@')[1] == "broadcast" and key != "status@broadcast":
                            print Fore.CYAN + "BROADCAST LIST CHAT", key + Fore.RESET
                            report_med += "<tr><th>Broadcast List</th><th><a href=\"report_broadcast_list_" + key + ".html" + "\" target=\"_blank\">  " + key + " " + "</a></th></tr>"
                            report_html = "./reports/report_broadcast_list_" + key + ".html"
                            arg_group = ""
                            arg_user = key
                        sql_string_copy = sql_string + " AND messages.key_remote_jid = '" + key + "'"
                        sql_consult_copy = cursor.execute(sql_string_copy)
                        messages(sql_consult_copy, sql_string_copy)
                    if args.report:
                        index_report(report_med, "./reports/index.html")
                    exit()

                sql_consult = cursor.execute(sql_string)
                messages(sql_consult, sql_string)
            except Exception as e:
                print "Error:", e

        elif args.key:
            decrypt(args.database, args.key)

        elif args.info:
            names("wa.db")
            db_connect(args.database)
            sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, " \
                         "latitude, longitude, remote_resource FROM messages;"
            sql_consult = cursor.execute(sql_string)
            info(sql_consult)

        elif args.extract:
            db_connect(args.database)
            print "Calculating number of images to extract"
            epoch_start = "0"
            """ current date in Epoch milliseconds string """
            epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

            if args.time_start:
                epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
            if args.time_end:
                epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))

            sql_count = "SELECT COUNT(*) FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp" \
                        " BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + " AND messages.media_wa_type IN (1, 3, 9, 13);"
            cursor.execute(sql_count)
            result = cursor.fetchone()
            print result[0], "Images found"
            sql_string_extract = "SELECT messages.key_id, messages.media_wa_type, messages.thumb_image, messages.raw_data, messages.timestamp, message_thumbnails.thumbnail FROM messages LEFT JOIN message_thumbnails " \
                                 "ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + " AND messages.media_wa_type IN (1, 3, 9, 13);"
            sql_consult_extract = cursor.execute(sql_string_extract)
            extract(sql_consult_extract, result[0])

        elif args.database:
            names("wa.db")
            db_connect(args.database)

