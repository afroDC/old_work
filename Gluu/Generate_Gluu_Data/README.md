Used to generate roughly 1.2 GB's of ldif data for testing a robust Gluu Server.

Download each file to your terminal:

```
wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Generate_Gluu_Data/company_names.txt && wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Generate_Gluu_Data/countries.txt && wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Generate_Gluu_Data/firstnames.txt && wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Generate_Gluu_Data/genUsersToLDAP.py && wget https://raw.githubusercontent.com/afroDC/Dev/master/Gluu/Generate_Gluu_Data/lastnames.txt
```

Change the `hosts` for each node and the password to the directory manager password in `genUsersToLDAP.py` to match your own and simply run the following:

It requires ldap3:

```
pip install ldap3
```
Then run the script:

```
python genUsersToLDAP.py
```

The script will automatically parse and grab the top of the inum, and place all entries into `ou=people`. This will take a while, but it's an easy way to upload a lot of users for testing functionality. All user passwords default to `secret` but can be changed.
