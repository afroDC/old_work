Please refer to the [wiki page]() for futher instructions on the functionality and use of these files.

To run the script, simply provide the file location and then the ip addresses of your servers in the proper order. Node 1, Node 2 and Node 3.

Let's assume I have 3 servers with the following IP address:

node_01 = 1.1.1.1  
node_02 = 2.2.2.2  
node_03 = 3.3.3.3  

```
python stunnel_conf.py node_01_stunnel.conf 1.1.1.1 2.2.2.2 3.3.3.3
python stunnel_conf.py node_02_stunnel.conf 1.1.1.1 2.2.2.2 3.3.3.3
python stunnel_conf.py node_03_stunnel.conf 1.1.1.1 2.2.2.2 3.3.3.3
```

Please note that node_01 must have the same stunnel configuration and redis configuration. Do no mix them up.
