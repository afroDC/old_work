import socket
import redis
import subprocess
import time

# Change this to where you cloned duplicator
# Clone the github repo https://github.com/agnoster/duplicator
# As far as I know, the dependencies are 'apt install npm','npm install npm, colors, bufferedstreams'

duplicator = "/root/duplicator/bin/duplicator"

#Check the health of Redis and TCP. Return False if either are down.

class NetHealth():
    host = '127.0.0.1'
    port = 7003

    def run(self):

        #Default host values for testing. Ideally this would be more algorithmic

        host = NetHealth.host
        port = NetHealth.port
        r = redis.Redis(host='localhost', port=7003, db=0)
        try:
            r.ping()
            print("It's working.")

        except:
            print("Couldn't connect.")
            return False


#Switch Duplicator to the alternative redis-server

def failoverSwitch():
    health = NetHealth()

    # If the NetHealth returns False on a poor connection, switch to a healthy node.
    # I would like to add another check here to see what other node is responsive, then reformat the duplicator command
    # duplicator -f {forwardhost:port} -d {duplicatehost:port} -p {port to listen on} [-i {ethernet interface}]
    # Furthermore, modifying and increasing that amount of servers that duplicator can interact with would be ideal.
    # Currently you can point the duplicate host at another duplicator instance and add more nodes that way.

    if health.run() == False:
        cmd = "ps -auxww | grep node | awk '{print $2}' | xargs kill -9"
        ps = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT)
        output = ps.communicate()[0]
        print output
        subprocess.Popen([duplicator, "-f", "localhost:7004", "-p", "2222"])
        NetHealth.port=7004
        # Currently the system fails if you try to duplicate to a redis instance that is down.
        # I would like another function to continue to monitor the lost instance, and reinitialize it if it comes back online.

    #Continuously run in the background, every second to see if primary node is fine
    else:
        time.sleep(1)
        failoverSwitch()

#Start the switch to monitor net health

failoverSwitch()
