from flask import request, Flask, jsonify, make_response
from flask_mysqldb import MySQL
import table_users as users

app = Flask(__name__)

#config mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'password'
app.config['MYSQL_DB'] = 'farming_assistant'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

#initialize mysql
mysql = MySQL(app)

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
    print(query)
    #execute query
    cur.execute(query) 
    
    #commit to the DB
    mysql.connection.commit()

    #close the connection
    cur.close()

    return ('User registered')

#@app.route('/login')

if __name__ == '__main__':
    app.run(host = '192.168.31.176',debug=True)