"""
Email details

Encapsulate Email address and Password under the same roof

properties:
1) user email address
2) user password
"""

class EmailDetails:
    def __init__(self, user_email_address, user_password):
        self.__user_email_address = user_email_address
        self.__user_password = user_password

    @property
    def user_email_address(self):
        return self.__user_email_address

    @user_email_address.setter
    def user_email_address(self, user_email_address):
        if user_email_address != None:
            self.__user_email_address = user_email_address

    @property
    def user_password(self):
        return self.__user_password

    @user_password.setter
    def user_password(self, user_password):
        if(user_password != None):
            self.__user_password = user_password