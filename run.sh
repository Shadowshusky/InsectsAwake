#!/bin/bash

APP_PATH=`dirname $0`
cd ${APP_PATH}

DB=/data/db

option=$1
[ -z "$option" ] && option=start


start(){
    nohup mongod --port 27017 --dbpath=${DB} --auth  > ${APP_PATH}/logs/db.log &
    nohup python ./InsectsAwake.py > ${APP_PATH}/logs/log.log &
}

stop(){
    python_manage=`ps -ef | grep "InsectsAwake.py" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
    for pid in ${python_manage}
    do
    kill -9 ${pid}
    done

    mongo_pid=`ps -ef | grep "mongod" | grep -v "$0" | grep -v "grep" | awk '{print $2}'`
    for pid in ${mongo_pid}
    do
    kill -9 ${pid}
    done
}

case ${option} in
    start)
    echo "Starting  Now......"
    start
    echo "Starting  Finished"
    ;;
    stop)
    echo "Stopping  Now......"
    stop
    echo "Stopping  Finished"
    ;;
    restart)
    echo "Restart  Now......"
    stop
    start
    echo "Restart  Finished"
    ;;
    *)
esac
