Used to generate roughly 1.2 GB's of ldif data for testing a robust Gluu Server.

Change the inum in `genData.py` to match your own and simply run the following:

```
python genData.py > example.ldif
```
To create an ldif you can use to upload to OpenLDAP.

Alternatively you can write the users directly to LDAP by using the `genUsersToLDAP.py`.

Change the following at the top of the script:

```
host = '<host>:1636'
...
password = '<pass>'
```

The script will automatically parse and grab the top of the inum, and place all entries into `ou=people`. This will take a while, but it's an easy way to upload a lot of users for testing functionality. All user passwords default to `secret` but can be changed.
