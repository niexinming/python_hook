from flask import Flask
from flask import request
import subprocess
import shlex
import os
import psycopg2
from jinja2 import Template
import base64
import pickle

app = Flask(__name__)

@app.route('/pic',methods=['GET'])
def mypickle():
    base64_input=request.args.get('data')
    deinput=base64.b64decode(base64_input)
    pickle.loads(deinput)
    return "ok"

@app.route('/tpl',methods=['GET'])
def mytemplate():
    myinput=request.args.get('url')
    output=""
    if myinput :
        output="Your input: {}".format(myinput)
    else:
        output="Your input: {}".format('<empty>')
    template = Template(output)
    return template.render()


@app.route('/subprocess',methods=['GET'])
def mysubprocess():
    cmd = request.args.get('cmd')
    cmd = shlex.split(cmd)
    subprocess.Popen(cmd)
    return "ok subprocess"

@app.route('/os',methods=['GET'])
def myos():
    cmd = request.args.get('cmd')
    os.system(cmd)
    return "ok os"


@app.route('/open',methods=['GET'])
def myopen():
    path = request.args.get('path')
    f=open(path,'r')
    a=f.read()
    f.close()
    return a

@app.route('/create',methods=['GET'])
def mycreate():
    path = request.args.get('path')
    content=request.args.get('c')
    f=open(path,'w')
    f.write(content)
    f.close()
    return "ok"


@app.route('/del',methods=['GET'])
def mydel():
    path = request.args.get('path')
    os.remove(path)
    return "ok"


@app.route('/sql',methods=['GET'])
def mysql():
    re=""
    sql = request.args.get('sql')
    conn = psycopg2.connect(dbname="TDADB")
    cur = conn.cursor()
    cur.execute(sql)
    rows = cur.fetchall()
    for row in rows:
        re=str(row)

    return "ok "+re


if __name__ == '__main__':
    
    app.run(use_debugger=True, debug=True,host='0.0.0.0')
