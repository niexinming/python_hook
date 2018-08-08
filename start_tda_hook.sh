export PYTHONPATH='./hook'
PYTHONPATH='./hook'

sudo auditctl -D

mypid=`ps -ax | grep 'test_flask.py' | grep -v 'grep' | awk '{print $1}'`

if  [ "$mypid" != "" ] ;then
    kill $mypid
fi

sleep 2

python test_flask.py &

sleep 1

mypid=`ps -ax | grep 'test_flask.py' | grep -v 'grep' | awk '{print $1}'`

sudo auditctl -a exclude,always -F msgtype!=PATH -F msgtype!=SYSCALL
sudo auditctl -a always,exit -F pid=$mypid
