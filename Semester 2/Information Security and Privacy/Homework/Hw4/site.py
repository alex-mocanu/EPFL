#!/usr/bin/env python3
import os
import sys
import populate
from flask import g
from flask import Flask, current_app
from flask import render_template, request, jsonify
import pymysql


app = Flask(__name__)
username = "root"
password = "root"
database = "hw4_ex3"

def execute_query(db, cursor, sql_query):
    '''
    Execute the an SQL query on a database
    input:  db - database to be queried
            cursor - a database cursor
            sql_query - SQL query to be executed
    output: the result of the query
    '''
    cursor.execute(sql_query)
    db.commit()

    rows = []
    while True:
        row = cursor.fetchone()
        if row is None:
            break
        else:
            rows.append(row)

    return rows


## This method returns a list of messages in a json format such as
## [
##  { "name": <name>, "message": <message> },
##  { "name": <name>, "message": <message> },
##  ...
## ]
## If this is a POST request and there is a parameter "name" given, then only
## messages of the given name should be returned.
## If the POST parameter is invalid, then the response code must be 500.
@app.route("/messages", methods=["GET","POST"])
def messages():
    with db.cursor() as cursor:
        # Retrieve all data in default mode
        sql_query = 'select name, message from messages'
        # Treat POST request
        if request.method == 'POST':
            form = request.form
            # Check that at most a 'name' parameter is given
            if len(form) > 0 and 'name' in form:
                # Retrieve data corresponding to the name
                sql_query += (" where name='%s'" % form['name'])
        # Make request to database
        data = execute_query(db, cursor, sql_query)
        # Construct JSON
        json = [{'name': name, 'message': message} for name, message in data]

        return jsonify(json), 200


## This method returns the list of users in a json format such as
## { "users": [ <user1>, <user2>, ... ] }
## This methods should limit the number of users if a GET URL parameter is given
## named limit. For example, /users?limit=4 should only return the first four
## users.
## If the parameter given is invalid, then the response code must be 500.
@app.route("/users", methods=["GET"])
def contact():
    with db.cursor() as cursor:
        # Retrieve all data in default mode
        sql_query = 'select * from users'
        # Get request parameters
        args = request.args
        # Check that at most a 'limit' parameter is given
        if 'limit' in args:
            try:
                # Check the validity of the request
                num_users = int(args['limit'])
            except:
                return 'Wrong request', 500
            if num_users < 0:
                return 'Wrong request', 500
            sql_query += ' limit ' + str(num_users)
        # Make the request to the database
        data = execute_query(db, cursor, sql_query)
        # Construct JSON
        json = {'users': data}

    return jsonify(json), 200


if __name__ == "__main__":
    seed = "randomseed"
    if len(sys.argv) == 2:
        seed = sys.argv[1]

    db = pymysql.connect("localhost",
                username,
                password,
                database)
    with db.cursor() as cursor:
        populate.populate_db(seed,cursor)
        db.commit()
    print("[+] database populated")

    app.run(host='0.0.0.0',port=80)
