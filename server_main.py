from flask import request, Flask, jsonify, make_response
from flask_mysqldb import MySQL
import table_users as users
import random

app = Flask(__name__)

#config mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'farming_assistant'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#initialize mysql
mysql = MySQL(app)

#inititalize session tracking variable session:username
SESSION = {}
SESSION_ID = -1

@app.route('/')
def home():
    return ('API working')

@app.route('/getNames')
def getUsernames():
    
    #define cursor
    cur = mysql.connection.cursor()

    data = []
    query = 'SELECT * FROM ' + users.TABLE_NAME 

    result = cur.execute(query)

    while result > 0:
        row = cur.fetchone()
        data.append(row)
        result = result - 1
    
    cur.close()
    return jsonify(data)

@app.route('/registration',methods=['POST'])
def resgistration():
    
    #get data from payload
    data = request.get_json()
    username = data[users.USERNAME]
    name = data[users.NAME]
    dob = data[users.DOB]
    location = data[users.LOCATION]
    phoneNo = data[users.PHONE_NO]
    email = data[users.EMAIL]
    password = data[users.PASSWORD]
    typ = data[users.TYPE]

    #define cursor
    cur = mysql.connection.cursor()

    query = 'INSERT INTO ' + users.TABLE_NAME + ' VALUES(\"'+ username + '\",\"' + name + '\",\"' + dob + '\",\"' + location + '\",\"' + phoneNo + '\",\"' + email + '\",\"' + password + '\",' + typ + ');' 
    # print(query)
    try:
        #execute query
        cur.execute(query) 
    
        #commit to the DB
        mysql.connection.commit()

        #close the connection
        cur.close()

        print("successfully inserted")
        return ('201')
        
    except mysql.connection.Error as error:
        print("Error registering" + error)
        return ('500')

@app.route('/login',methods=['POST'])
def login():
    global SESSION,SESSION_ID
    data = request.get_json()
    username = data[users.USERNAME]
    password = data[users.PASSWORD]

    #define cursor
    cur = mysql.connection.cursor()

    query = "SELECT " + users.PASSWORD + " from " + users.TABLE_NAME + " WHERE " + users.USERNAME + " = " + '\'' + username + '\';'
    # print(query)

    #execute query
    result = cur.execute(query) 

    ret_val = -1

    while result > 0:
        row = cur.fetchone()
        if row[users.PASSWORD] == password:
            found = False
            for ses,us in SESSION.items():
                if us == username:
                    ret_val = ses
                    found = True
                    break

            if found == False:
                SESSION[SESSION_ID] = username
                ret_val = SESSION_ID
                SESSION_ID = SESSION_ID + 1
        
        result = result - 1
        
    #close connection
    cur.close()

    # print(str(ret_val))

    return (str(ret_val))


if __name__ == '__main__':
    SESSION_ID = random.randint(1,1000)
    app.run(host = '192.168.1.25',debug=True)
