"""
findBigMail.py
Mayank Gureja
02/22/2013
"""

import getpass
from imaplib import IMAP4_SSL
import email
import sys
import re


def connect():
    """
    Connect to mailbox using IMAP and ssl
    """

    mailBox = IMAP4_SSL('imap.gmail.com')

    if TESTING:
        mailBox.login("sapphirephoenix", getpass.getpass())
    else:
        mailBox.login(raw_input("\nUsername: "), getpass.getpass())

    result, data = mailBox.select('INBOX', True)  # INBOX [Gmail]/All Mail

    if result == "OK":
        print "\n* Connected to mailbox! *\n"
    else:
        print "\nERROR: Could not connect to mailbox\n"
        print "\n* Exiting... *\n"
        sys.exit(1)

    return mailBox


def search(folderName):
    """
    Search through folder and get all UIDs
    """

    result, data = mailBox.select(folderName, True)

    if TESTING:
        searchResult, uid = mailBox.uid('SEARCH', None, 'UNSEEN')
    else:
        searchResult, uid = mailBox.uid('SEARCH', None, 'ALL')

    number_messages = len(uid[0].split(' ')) if uid[0] != "" else 0
    if number_messages == 0:
        print "\nERROR: No messages found in %s\n" % folderName
        print "\n* Exiting... *\n"
        sys.exit(0)
    print "\nNumber of messages in %s: %d" % (folderName, number_messages)

    uidList = ""
    for i in uid[0].split(' '):
        if i.isdigit():
            uidList += i + ","
    uidList = uidList[:-1]

    return uidList


def getLargest(uidList):
    """
    Get UID of message with largest size
    """

    maxID = 0
    maxSize = 0

    result, data = mailBox.uid('FETCH', uidList, 'RFC822.SIZE')

    for item in data:
        uid = re.search('UID (\d+)', item)
        size = re.search('SIZE (\d+)', item)
        if uid and size:
            if size.group(1) > maxSize and uid.group(1) not in skippedList:
                maxID = uid.group(1)
                maxSize = size.group(1)

    skippedList.append(maxID)  # Message already checked once

    return maxID, maxSize


def getInfo(uid):
    """
    Get info about message
    """

    if TESTING:
        result, data = mailBox.uid('FETCH', uid, '(BODY.PEEK[HEADER])')
    else:
        result, data = mailBox.uid('FETCH', uid, 'RFC822')

    if result != "OK":
        print "\nERROR: Could not fetch message"
        return

    raw_email = data[0][1]
    email_message = email.message_from_string(raw_email)
    result, data = mailBox.uid('FETCH', uid, 'RFC822.SIZE')
    size = re.search('SIZE (\d+)', uid).group(1)

    print "\nInfo about message:"
    print "-------------------------------------"
    print "From:", email_message['From']
    print "To:", email_message['To']
    print "Cc:", email_message['Cc']
    print "Bcc:", email_message['Bcc']
    print "Subject:", email_message['Subject']
    print "Date:", email_message['Date']
    print "Message Size:", size


def delete(uid, folderName, switch):
    """
    Delete message in folder
    switch: Leave blank or put 'f' to suppress confirmation
    """

    if switch != "f":
        choice = str(raw_input("\nDo you want to delete this message? (Y/N): "))
    else:
        choice = "Y"

    if choice.upper() == "Y":
        result, data = mailBox.select(folderName, False)
        result, data = mailBox.uid('STORE', uid, '+FLAGS', '\\Deleted')
        mailBox.expunge()

        if result != "OK":
            print "* An error occured. Message was NOT deleted *"
    else:
        print "* Not deleting this message *"

    return result


def mergeFolders():
    """
    Merge 2 folders into 1. Does not create a new folder,
    simply moves messages from one folder to another folder
    """

    result, data = mailBox.list()
    if result != "OK":
        print "\nERROR: Could not get list of folders in mailbox\n"
        print "\n* Exiting... *\n"
        sys.exit(1)

    folderList = []
    print "\nList of folders:"
    print "---------------------"
    for item in data:
        folderName = item.split()[-1].replace("\"", "")
        if not "Gmail" in folderName:
            folderList.append(folderName)
            print folderName

    srcFolder = str(raw_input("\nEnter source folder name EXACTLY: "))
    if srcFolder not in folderList:
        print "\nERROR: Incorrect source folder name\n"
        print "\n* Exiting... *\n"
    destFolder = str(raw_input("\nEnter destination folder name: "))
    if destFolder not in folderList:
        print "\nERROR: Incorrect destination folder name\n"
        print "\n* Exiting... *\n"

    uidList = search(srcFolder)

    result1 = ""
    result2 = ""
    flag1 = True
    flag2 = True
    result, data = mailBox.select(srcFolder, False)

    for item in uidList.split(","):

        result1, data = mailBox.uid('COPY', item, destFolder)
        if result1 == "OK":
            result2 = delete(item, srcFolder, "f")

        if result1 != "OK":
            flag1 = False
        if result2 != "OK":
            flag2 = False

    if flag1 == flag2 == True:
        print "\n* Merge successful *\n"
    else:
        if flag1 == False:
            print "\nERROR: Could not copy to %s while merging folders\n" % destFolder
        if flag2 != False:
            print "\nERROR: Could not delete message from source folder %s\n" % srcFolder


"""
Main
"""

TESTING = False

print "************ MENU ************"
print "1. Delete largest emails"
print "2. Merge folders"
print "******************************"

menuChoice = int(raw_input("\nChoose a number: "))

mailBox = connect()
if menuChoice == 1:
    skippedList = []  # List of UIDs already processed
    uidList = search("INBOX")

    choice = "Y"
    while(choice.upper() == "Y"):
        maxID, maxSize = getLargest(uidList)
        if not maxID:  # Empty search list
            print "No more messages found in INBOX"
            choice = "N"
            continue
        getInfo(maxID, maxSize)
        result = delete(maxID, "INBOX")
        if result == "OK":
            print "* Message deleted *"

        choice = str(raw_input("\nMove onto next largest message? (Y/N) "
                               "N will exit the program: "))

        if choice.upper == "Y":
            print "* Moving onto next largest message... *"
elif menuChoice == 2:
    mergeFolders()
else:
    print "\nERROR: Wrong choice\n"


print "\n* Exiting... *\n"
mailBox.close()
mailBox.logout()
