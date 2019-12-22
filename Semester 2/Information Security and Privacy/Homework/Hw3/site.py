#!/usr/bin/env python3
import os
import sys
import populate
from flask import g
from flask import Flask,current_app
from flask import render_template,request
import pymysql
app=Flask(__name__)
if len(sys.argv)!=2:
 print("email required as first argument")
 sys.exit(1)
email=sys.argv[1]
config={}
with open("credentials.cfg","r")as f:
 exec(f.read(),config)
keys=["TOKEN","DATABASE1","USERNAME1","USER_PWD1"]
keys+=["DATABASE2","USERNAME2","USER_PWD2"]
if not all(k in config for k in keys):
 print("not enough config keys: "+str(config.keys()))
 sys.exit(1)
token=config["TOKEN"]
def get_db1():
 db1=getattr(g,'_database1',None)
 if db1 is None:
  db1=pymysql.connect("localhost",config["USERNAME1"],config["USER_PWD1"],config["DATABASE1"])
  cursor1=db1.cursor()
  populate.populate_db1(cursor1,token,email)
  print("database 1 is populated")
  db1.commit()
  g._database1=db1
 return db1
def get_db2():
 db2=getattr(g,'_database2',None)
 if db2 is None:
  db2=g._database=pymysql.connect("localhost",config["USERNAME2"],config["USER_PWD2"],config["DATABASE2"])
  cursor2=db2.cursor()
  populate.populate_db2(cursor2,token,email)
  print("database 2 is populated")
  db2.commit()
  g._database2=db2
 return db2
@app.route("/messages",methods=["GET","POST"])
def messages():
 with get_db2().cursor()as cursor:
  sql="SELECT name,message FROM contact_messages "
  if request.method=="GET":
   cursor.execute(sql)
   return render_template("messages.html",show=False,messages=cursor.fetchall())
  name=request.form["name"]
  if name is not None and name is not "":
   sql+="WHERE name LIKE '"+name+"'"
  cursor.execute(sql)
  results=cursor.fetchall()
  if len(results)==0:
   return render_template("messages.html",show=True,exists=False)
  else:
   return render_template("messages.html",show=True,exists=True)
@app.route("/personalities",methods=["GET"])
def personalities():
 with get_db1().cursor()as cursor:
  sql="SELECT id,name FROM personalities "
  if request.args.get('id')is not None:
   sql+="WHERE id = '"+request.args.get('id')+"'"
  cursor.execute(sql)
  return render_template("personalities.html",personalities=cursor.fetchall())
@app.route("/",methods=["GET","POST"])
def contact():
 template="index.html"
 if request.method=="GET":
  return render_template(template)
 email=request.form['email']
 name=request.form['name']
 message=request.form['message']
 if email=="":
  error="Empty email"
  expl="You already have zero privacy. Get over it.'"
  return render_template(template,error=error,expl=expl)
 if name=="":
  error="Empty name"
  expl="'It is the first responsibility of every citizen to question authority.'"
  return render_template(template,error=error,expl=expl)
 if message=="":
  error="Empty message"
  expl="'Saying nothing... sometimes says the most.'"
  return render_template(template,error=error,expl=expl)
 sql="INSERT INTO contact_messages (name,mail,message) VALUES (%s,%s,%s);"
 with get_db1().cursor()as cursor:
  cursor.execute(sql,(name,email,message))
 return render_template(template,success="Message sent!")
if __name__=="__main__":
 with app.app_context():
  print(current_app.name)
  get_db1()
  get_db2()
  current_app.run(host='0.0.0.0',port=80)
