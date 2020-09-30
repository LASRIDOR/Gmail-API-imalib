from time import sleep
import ConnectorGmail
import RepeatedTimer
import EmailDetails
from configparser import ConfigParser
import json
import email
import os
from email.header import decode_header

"""
Connector Manager

properties:
1)path_config_file
2)connector_to_gmail (ConnectorGmail object)
3)path_json_files - location to save JSON files
4)iteration_period - interval
5)stimulant - (RepeatedTimer object)
6)flag for new configuraion file
7)lost file name (in case of failing path the program opens new file of losing mails (same location of program))
8)smtp_server

logic:
1) Decode Config File To Connect Gmail Service
2) Periodically Fetch Emails From Gmail And Store Them As Json Files
3) Save Unread Messages As Json File 
4) From List Of unread messages IDs To Json File
5) Make Json File From Dictionary Of Email Details
6) Clean Name Of Json File
7) Force Stop Program
8) On Fail Service Connection (events)
9) On Mail Service Connected  (events)
"""

class ConnectorManager(object):
    def __init__(self, smtp_server, path_config_file):
        self.smtp_server = smtp_server
        self.path_config_file = path_config_file
        self.__connector_to_gmail = ConnectorGmail.ConnectorGmail(smtp_server, None, self.on_FailServiceConnection, self.on_MailServiceConnected)
        self.__path_json_files = None
        self.__iteration_period = None
        self.__stimulant = None
        self.__v_new_configuration = None
        self.__decodeConfigFileToConnectGmailService()
        self.__lost_file_name = "Lost Mails"
        self.__makeNewFolder(self.__lost_file_name)
        self.__v_valid_config_file = None

    def __decodeConfigFileToConnectGmailService(self):
        """Decoding config file from the path that have given when initiating the class and then:

        1) at the start google gmail connector doesnt have API mail service so the program gives him email address and password
        and trying to make a connection (watch ** to see what happen when cant make a connection)
        2) while fetching config file can be changed at any time including change email address, password, interval and path
        ** during a fail with the mail service config file will be read and at the time when new details will come flag will
        be raised ( __v_new_configuration ) to try to get service

        at any change:
        a) RepeatedTimer will be updated with the new interval
        b) Connector will be updated with the new email details
        c) ConnectorManager will be updated with the new path (JSON files's save location)
        """
        self.__v_valid_config_file = False
        temp_email_address = None
        temp_password = None
        temp_path_json_files = None
        temp_iteration_period = None
        temp_user_email_details = None

        while self.__v_valid_config_file == False:
            try:
                parser_mail_service = ConfigParser()
                parser_mail_service.read(self.path_config_file)

                temp_email_address = parser_mail_service.get("Credentials", "email")
                temp_password = parser_mail_service.get("Credentials", "password")
                temp_path_json_files = parser_mail_service.get("Path", "address")
                temp_iteration_period = int(parser_mail_service.get("IterationPeriod", "intervals"))
                temp_user_email_details = EmailDetails.EmailDetails(temp_email_address, temp_password)

                self.__v_valid_config_file = True
            except Exception as e:
                self.__v_valid_config_file = False
                print('An error occurred while decoding the config file: %s' % str(e))
                sleep(3)


        if self.__stimulant is not None:
            if(temp_iteration_period != self.__stimulant.interval):
                self.__stimulant.interval = temp_iteration_period

        self.__iteration_period = temp_iteration_period
        self.__path_json_files = temp_path_json_files

        if self.__connector_to_gmail.user_email_details == None:
            self.__v_new_configuration = True
            self.__connector_to_gmail.user_email_details = temp_user_email_details
            self.__connector_to_gmail.GetService()

        else:

            if(self.__connector_to_gmail.user_email_details.user_email_address != temp_email_address
                    or self.__connector_to_gmail.user_email_details.user_password != temp_password):
                self.__connector_to_gmail.user_email_details = temp_user_email_details
                self.__v_new_configuration = True

                if self.__connector_to_gmail.v_mail_service_is_connected == True:
                    self.__connector_to_gmail.v_mail_service_is_connected = False
                    self.__connector_to_gmail.GetService()

            else:
                self.__v_new_configuration = False

    def PeriodicallyFetchEmailsFromGmailAndStoreThemAsJsonFiles(self, long_running_times=None):
        """"this program: periodically every 10 seconds fetch emails from Gmail and store them as json files.
         For each iteration get all emails that are marked as unread and fetch them.

         args:
         1) long-running_times - at the long-time running how many times you want the whole program to run (intervals * long_running_times)
         2) interval - period iteration for fetching emails

         Pay Attention:
         for unlimited time of fetching just let long_running_time be None value.
        """
        self.__stimulant = RepeatedTimer.RepeatedTimer(self.__iteration_period, self.__saveUnreadmessagesAsJsonFile)  # it auto-starts, no need of rt.start()

        if(long_running_times != None):
            try:
                sleep(self.__iteration_period*long_running_times)  # your long-running job goes here..
            finally:
                self.__stimulant.Stop()  # better in a try/finally block to make sure the program ends!

    def __saveUnreadmessagesAsJsonFile(self):
        """this program: fetch emails from Gmail and store them as files.
        gets all emails that are marked as unread and fetch them.

        For each email that have been fetched:
        1. Marked the email as read at the Gmail inbox (In order not to fetch them again on the next iteration) .
        2. Save the email as JSON file - File name should be - email time + MessageID
        3. Email JSON file structure:
            a. Sender
            b. Receiver
            c. Subject
            d. Body
        """

        self.__decodeConfigFileToConnectGmailService()
        list_of_unreadmessageids_from_inbox = self.__connector_to_gmail.ListMessagesIdsMatchingQueryWithLabels( 'inbox', '(UNSEEN)')
        self.__fromListOfUnreadmessagesIDsToJsonFile(list_of_unreadmessageids_from_inbox)

    def __fromListOfUnreadmessagesIDsToJsonFile(self, list_of_unreadmessagesIDs):
        """For each email that have been fetched and listed:
        1. Marked the email as read at the Gmail inbox (In order not to fetch them again on the next iteration) .
        2. Save the email as JSON file - File name should be - email time + MessageID
        3. Email JSON file structure:
            a. Sender
            b. Receiver
            c. Subject
            d. Body

            {
                'Sender': '"email.com" <name@email.com>',
                'Receiver' : '"email.com" <name@email.com>'
	             'Subject': Email Subject,
	            'Message_body': Email Content
	        }
        """

        if (bytes.__len__(list_of_unreadmessagesIDs) > 0):
            id_list = list_of_unreadmessagesIDs.split()
            first_email_id = 0
            latest_email_id = list.__len__(id_list)
            for i in range(latest_email_id, first_email_id, -1):
                temp_dictionary_for_json_file = {}
                temp_email_sender = None
                temp_email_receiver = None
                temp_email_subject = None
                temp_email_body = None
                temp_email_date = None
                temp_email_MessageID = None

                message_data = self.__connector_to_gmail.GetMessage(int(id_list[i - 1]), '(RFC822)')

                for response in message_data:
                    if isinstance(response, tuple):
                        msg = email.message_from_bytes(response[1])
                        temp_email_subject = decode_header(msg["Subject"])[0][0]
                        if isinstance(temp_email_subject, bytes):
                            temp_email_subject = temp_email_subject.decode()
                        temp_email_sender = msg.get("From")
                        temp_email_receiver = msg.get("To")
                        temp_email_date = msg.get("Date")
                        temp_email_MessageID = msg.get("Message-ID")
                        if msg.is_multipart():
                            for part in msg.walk():
                                temp_email_body_part = None
                                content_type = part.get_content_type()
                                content_disposition = str(part.get("Content-Disposition"))
                                try:
                                    temp_email_body_part = part.get_payload(decode=True).decode()
                                except:
                                    pass
                                if content_type == "text/plain" and "attachment" not in content_disposition:
                                    if temp_email_body == None:
                                        temp_email_body = temp_email_body_part
                                    else:
                                        temp_email_body += temp_email_body_part
                                        temp_email_body += "\n\n"
                                elif "attachment" in content_disposition:
                                    pass

                        else:
                            content_type = msg.get_content_type()
                            temp_email_body_part = msg.get_payload(decode=True).decode()

                            if content_type == "text/plain":
                                # print only text email parts
                                if temp_email_body == None:
                                    temp_email_body = temp_email_body_part
                                else:
                                    temp_email_body += temp_email_body_part
                                    temp_email_body += "\n\n"

                            if content_type == "text/html":
                                pass
                temp_dictionary_for_json_file = {"Sender": temp_email_sender,
                                                     "Receiver": temp_email_receiver,
                                                     "Subject": temp_email_subject,
                                                     "Body": temp_email_body}
                self.__makeJsonFileFromDictionaryOfEmailDetails(temp_dictionary_for_json_file, temp_email_date + ' ' + temp_email_MessageID)

    def __makeJsonFileFromDictionaryOfEmailDetails(self, dictionary_email_details, json_file_name):
        """" Save the email as JSON file - File name should be - email time + MessageID
             the JSON file will be saved in the same file where the program will be running from

             args:
             dictionary_email_details - dictionary to save in json_file
             json_file_name - the name of the json file

             exception:
             incase of failure at the path to prevent losing the dictionary after fetching it and
             marking it as READ and saving it in dictionary the dictionary will be saved as lost one at Program File
             (like C:\\)
        """

        address_to_save_file = self.__path_json_files
        json_file_name = self.__cleanNameOfJsonFile(json_file_name)
        json_file_name += '.json'
        address_to_save_file += '\\'
        address_to_save_file += json_file_name

        to_save = json.dumps(dictionary_email_details, ensure_ascii=False, indent=2)
        try:
            with open(address_to_save_file, 'wb') as outfile:
                outfile.write(to_save.encode("utf-8"))

        except Exception as e:
            lost_address_to_save_file = os.getcwd()
            lost_address_to_save_file += '\\'
            lost_address_to_save_file += self.__lost_file_name
            lost_address_to_save_file += '\\'
            lost_address_to_save_file += json_file_name

            with open(lost_address_to_save_file, 'wb') as outfile:
                outfile.write(to_save.encode("utf-8"))
            print('An error occurred while saving to json file (file saved at lost mail file): %s' % str(e))

    def __cleanNameOfJsonFile(self, json_file_name):
        """" this program earase all the forbiden char in windows file names (json_file_name)

        args:
        json_file_name

        return s json_name_file (free of forbidden char)
        """

        json_file_name = str(json_file_name).replace('/', ' ')
        json_file_name = str(json_file_name).replace('\\', ' ')
        json_file_name = str(json_file_name).replace(':', ';')
        json_file_name = str(json_file_name).replace('?', ' ')
        json_file_name = str(json_file_name).replace('\"', ' ')
        json_file_name = str(json_file_name).replace('<', ' ')
        json_file_name = str(json_file_name).replace('>', ' ')
        json_file_name = str(json_file_name).replace('|', ' ')

        return json_file_name

    def ForceStopProgram(self):
        if self.__stimulant != None:
            self.__stimulant.Stop()

    def on_FailServiceConnection(self, *args, **kwargs):
        self.__v_new_configuration = False
        if self.__stimulant != None:
            self.__stimulant.Stop()

        while self.__v_new_configuration == False:
            self.__decodeConfigFileToConnectGmailService()
            sleep(2)

    def on_MailServiceConnected(self):
        if self.__stimulant != None:
            self.__stimulant.Start()

    def __makeNewFolder(self, folder_name):
        if not os.path.isdir(folder_name):
            # make a folder for this email (named after the folder name)
            os.mkdir(folder_name)