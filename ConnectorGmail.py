import imaplib

import Connector
import EmailDetails
import pydispatch
from pydispatch import Dispatcher

"""
ConnectorGmail
a connector to gmail mail service that has the ability to read messages from Gmail account

properties:
1) flag for connected service
2) mail service
3) server
4)user email details

logic:
1) Get service
2) List Messages IDs Matching Query With Labels 
3) Get Message
"""

class ConnectorGmail(Dispatcher, Connector.Connector):
    _events_ = ['on_fail_service_connection', 'on_mail_service_conneted']

    def __init__(self, smtp_server, user_email,on_FailService_connection, on_MailServiceConneted):
        Connector.Connector.__init__(self, smtp_server)
        self.__user_email_details = user_email
        self.bind(on_fail_service_connection=on_FailService_connection)
        self.bind(on_mail_service_conneted=on_MailServiceConneted)

    @property
    def user_email_details(self):
        return self.__user_email_details

    @user_email_details.setter
    def user_email_details(self, user_email):
        if user_email != None:
            self.__user_email_details = user_email

    def GetService(self):
        """"this program gets a mail service API from Gmail Acoount (needs Email adress And Password)

        Requirements:
        1) imap
        2) Less secure app access - need to be turned on thru the gmail accout otherwise google will block imap access
        (this active is not insecure the only thing its says is that whatever app that has the
        email address and password can get access to your account (access can be managed thru google 3rd party manager))

        the service will be saved as a class member to change google account change the class member email and password
        """
        while self.v_mail_service_is_connected == False:
            try:
                mail_service = imaplib.IMAP4_SSL(self.smtp_server)
                mail_service.login(self.user_email_details.user_email_address, self.user_email_details.user_password)

                self.emit('on_mail_service_conneted')
                self.v_mail_service_is_connected = True
                self.__mail_service = mail_service
            except Exception as e:
                self.v_mail_service_is_connected = False
                print('An error occurred while getting service: %s' % str(e))
                self.emit('on_fail_service_connection')

    def ListMessagesIdsMatchingQueryWithLabels(self, label_id, query):
        """List all Messages of the user's mailbox matching the query.

        Args:
          service: Authorized Gmail API service instance (saved as a class member).
          query: String used to filter messages returned.
          Eg.- 'from:user@some_domain.com' for Messages from a particular sender.
          label_ids: Only return Messages with these labelIds applied.

        Returns:
          List of MessagesIDs that match the criteria of the query with the labelsids.
        """
        if label_id is None:
            label_id = 'inbox'
        if query is None:
            query = '(UNSEEN)'
        try:
            self.__mail_service.select(label_id)
            typ, data = self.__mail_service.search(None, query)
            mail_ids = data[0]

            return mail_ids
        except Exception as e:
            print('An error occurred while getting the list of messages: %s' % str(e))

    def GetMessage(self, msg_id, message_parts):
        """Get a Message with given ID.

        Args:
          service: Authorized Gmail API service instance (saves as a class member).
          msg_id: The ID of the Message required.

        Returns:
          A Message.
        """
        if(message_parts == None):
            message_parts = '(RFC822)'
        try:
            type, data = self.__mail_service.fetch(str(msg_id), message_parts)

            return data
        except Exception as e:
            print('An error occurred while getting a message: %s' % str(e))