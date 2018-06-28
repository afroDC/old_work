Used to generate roughly 1.2 GB's of ldif data for testing a robust Gluu Server.

Change the `hosts` for each node and the password to the directory manager password in `genUsersToLDAP.py` to match your own and simply run the following:

It requires ldap3:

```
pip install ldap3
```

The script will automatically parse and grab the top of the inum, and place all entries into `ou=people`. This will take a while, but it's an easy way to upload a lot of users for testing functionality. All user passwords default to `secret` but can be changed.
