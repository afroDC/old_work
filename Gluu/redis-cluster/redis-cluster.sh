#! /bin/bash
### BEGIN INIT INFO
# Provides:		redis-cluster
# Required-Start:	$syslog
# Required-Stop:	$syslog
# Should-Start:		$local_fs
# Should-Stop:		$local_fs
# Default-Start:	2 3 4 5
# Default-Stop:		0 1 6
# Short-Description:	redis-server cluster launch
# Description:		Launching and estarting a redis-server in cluster configuration. 
### END INIT INFO


PATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin
DAEMON=/usr/bin/redis-server
NAME=redis-cluster
DESC="Deploy Redis Cluster configs from directories in /etc/redis/cluster/"
redis_cluster_dir='/etc/redis/cluster/'

set -e

ubuntu=true

if [ -f /etc/lsb-release ]; then
    ubuntu=true
elif [ -f /etc/redhat-release ]; then
    ubuntu=false
fi

start_redis()
{
    conf_dir=$(find ${redis_cluster_dir}* -maxdepth 0 -type d)

    if ! pgrep -x redis-server > /dev/null
    then
        echo "Starting $DESC ..."

        for conf in $conf_dir
        do
            path="$conf/"
            conf_file="$(echo $path | cut -d '/' -f 5)"
            conf_path="$path$(echo $path | cut -d '/' -f 5).conf"

            if redis-server $conf_path &
            then
                echo "Redis-server on port ${conf_file} started!"
            else
                echo "Redis-server failed to start!"
            fi
        done
    else
        echo "Redis is already running!"
    fi
}
start_stunnel()
{
    if ! pgrep -x stunnel > /dev/null
    then
        if stunnel /etc/stunnel/stunnel.conf
        then
            echo "Stunnel started!"
        else
            echo "Stunnel failed to start!"
        fi
    else
        echo "Stunnel already running!"
    fi
}

stop_redis()
{
    if pgrep -x redis-server > /dev/null
    then
        echo "Stopping $DESC ..."

        if [ "$ubuntu" = true ]
        then
            if /usr/bin/pkill redis-server
            then
                echo "Redis-server cluster stopped!"
            else
                echo "Failed stopping redis-server cluster!"
            fi
        else
            if /usr/bin/pkill redis-server
            then
                echo "Redis-server cluster stopped!"
            else
                echo "Failed stopping redis-server cluster!"
            fi
        fi
    else
        echo "Redis-server cluster is not running!"
    fi
}
stop_stunnel()
{
    if pgrep -x stunnel > /dev/null
    then
        if [ "$ubuntu" = true ]
        then
            if [ -f /var/run/stunnel.pid ]
            then
                if /usr/bin/pkill stunnel
                then
                    echo "Stunnel stopped!."
                else
                    echo "Failed stopping stunnel!"
                fi
            else
                echo "Stunnel is not running!"
            fi
        else
            if /usr/bin/pkill stunnel
            then
                echo "Stunnel stopped!."
            else
                echo "Failed stopping stunnel!"
            fi
        fi
    else
        echo "Stunnel is not running!"
    fi
}
case "$1" in
  start)
	start_redis
    start_stunnel
    ;;
  stop)
	stop_redis
    stop_stunnel
    ;;
  restart|force-reload)
	${0} stop
	${0} start
    ;;
  *)
	echo "Usage: /etc/init.d/$NAME {start|stop|restart|force-reload}" >&2
	exit 1
	;;
esac

exit 0
