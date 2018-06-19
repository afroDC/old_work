# oxAuth is available under the MIT License (2008). See http://opensource.org/licenses/MIT for full text.
# Copyright (c) 2018, Gluu
#
# Author: Yuriy Movchan, Chris Blanton
#

from org.xdi.service.cdi.util import CdiUtil
from org.xdi.oxauth.security import Identity
from org.xdi.model.custom.script.type.auth import PersonAuthenticationType
from org.xdi.oxauth.service import AuthenticationService
from org.xdi.util import StringHelper
from org.xdi.oxauth.service import UserService
from org.xdi.util.security import BCrypt

import java

class PersonAuthentication(PersonAuthenticationType):
    def __init__(self, currentTimeMillis):
        self.currentTimeMillis = currentTimeMillis

    def init(self, configurationAttributes):
        print "BCrypt Auth. Initialization"
        print "BCrypt Auth. Initialized successfully"
        return True   

    def destroy(self, configurationAttributes):
        print "BCrypt Auth. Destroy"
        print "BCrypt Auth. Destroyed successfully"
        return True

    def getApiVersion(self):
        return 1

    def isValidAuthenticationMethod(self, usageType, configurationAttributes):
        return True

    def getAlternativeAuthenticationMethod(self, usageType, configurationAttributes):
        return None

    def authenticate(self, configurationAttributes, requestParameters, step):

        authenticationService = CdiUtil.bean(AuthenticationService)

        if (step == 1):
            print "BCrypt Auth. Authenticate for step 1"

            identity = CdiUtil.bean(Identity)
            credentials = identity.getCredentials()

            user_name = credentials.getUsername()
            user_password = credentials.getPassword()

            logged_in = False

            if (StringHelper.isNotEmptyString(user_name) and StringHelper.isNotEmptyString(user_password)):
                userService = CdiUtil.bean(UserService)
                user = userService.getUser(user_name)
                hashed_stored_pass = user.getAttribute("userPassword")
                print(hashed_stored_pass)

                password_schema = ''

                # Determine password schema
                # Example: {BCRYPT}$2b$08$71gBXNKJ/iUBXqLjEdEXFesoUYQm5vrpKefi8YhV7ITGfAd9VNFaG
                for char in hashed_stored_pass:
                    if char == '{':
                        continue
                    if char == '}':
                        break
                    password_schema = password_schema + char
                    # Iterate for debugging
                    print password_schema

                # OpenDJ's SSHA(512)
                if 'SSHA' in password_schema:

                    # Returns True if authenticated on the backend
                    logged_in = authenticationService.authenticate(user_name, user_password)

                # Pattern match BCRYPT and rewrite to SSHA
                elif 'BCRYPT' in password_schema:
                    # Pull salt from the stored hashed password
                    salt = hashed_stored_pass[8:]
                    salt = salt.split("$")[3].strip()
                    salt = salt[0:22]
                    salt = '$2a$08$' + salt

                    # Create hash of challenge clear text password
                    challenge = BCrypt.hashpw(user_password,salt)

                    # Strip unnecessary revision and rounds from both hashed passwords for comparison.
                    challenge = challenge.split("$")[3].strip()
                    stored = hashed_stored_pass.split("$")[3].strip()

                    print("Challenge: " + challenge)
                    print("Stored:    " + stored)

                    # Compare the hashses and update hash
                    if challenge in stored:

                        # Users inputted password hashed matches the hashed password in the backend
                        # Therefore we update the users password to the backend's password schema
                        print("Updating hash..")
                        user.setAttribute("userPassword",user_password)
                        user = userService.updateUser(user)
                        print("Logging in..")

                        # Returns True
                        logged_in = authenticationService.authenticate(user_name)
                        return logged_in

                # Catch unknown schema types and output to oxauth_script.log
                # This script can be expanded to include
                else:
                    print("Unrecognized algorithm: " + password_schema)

            if (not logged_in):
                return False
            logged_in = authenticationService.authenticate(user_name)
            return logged_in
        else:
            return False

    def prepareForStep(self, configurationAttributes, requestParameters, step):
        if (step == 1):
            print "BCrypt Auth. Prepare for Step 1"
            return True
        else:
            return False

    def getExtraParametersForStep(self, configurationAttributes, step):
        return None

    def getCountAuthenticationSteps(self, configurationAttributes):
        return 1

    def getPageForStep(self, configurationAttributes, step):
        return ""

    def logout(self, configurationAttributes, requestParameters):
        return True
