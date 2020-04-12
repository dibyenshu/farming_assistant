from flask import request, Flask, jsonify, make_response
from flask_mysqldb import MySQL
from inspect import getmembers
import table_users as users
import table_user_crops as user_crops
import table_crop_properties as crop_properties
import random
import majority_voting as MV

#to store the list of crops
CROPS = []

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

        #new query to initialize the name of the user in user_crops database;
        query = 'INSERT INTO ' + user_crops.TABLE_NAME + ' VALUES(\"'+ username + '\",\"0\",\"0\",\"0\",\"0\",\"0\",\"0\");'
        print(query)

        #execute query2
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
                SESSION[str(SESSION_ID)] = username
                ret_val = SESSION_ID
                SESSION_ID = SESSION_ID + 1
        
        result = result - 1
        
    #close connection
    cur.close()

    print(str(ret_val))
    return (str(ret_val))

@app.route('/getCrops/<farmerSessionId>',methods=['GET'])
def getCrops(farmerSessionId):
    global SESSION,SESSION_ID,CROPS
    farmerUsername = SESSION[farmerSessionId]
    print(farmerUsername)
    #get cursor
    cur = mysql.connection.cursor()

    query = "select * from " + user_crops.TABLE_NAME + " where " + user_crops.USERNAME + " = " + "\'" + farmerUsername + "\'" + ";"
    print(query)

    cur.execute(query)

    row = cur.fetchone()

    response = ""

    for crop in CROPS:
        if(row[crop]== '1'):
            response += "," + crop 

    cur.close()

    #returns the list of crops registered by the user
    return (str(response)[1:])


@app.route('/addCrop/<farmerSessionId>',methods=['POST'])
def addCrop(farmerSessionId):
    global SESSION,SESSION_ID,CROPS
    farmerUsername = SESSION[farmerSessionId]
    data = request.get_json()

    cur = mysql.connection.cursor()

    query = "select * from " + user_crops.TABLE_NAME + " where " + user_crops.USERNAME + " = " + "\'" + farmerUsername + "\'" + ";" 
    print(query)

    cur.execute(query)
    row = cur.fetchone()
    print(row)

    print("debug here")

    cropLs = {}
    for crop in CROPS:
        boolVal = (row[crop]=="1") | (data[crop]=="1")
        if boolVal:
            cropLs[crop] = "1"
        else:
            cropLs[crop] = "0"

    query = "update " + user_crops.TABLE_NAME + " set " + user_crops.RICE + " = " + "\'" + cropLs[user_crops.RICE] + "\'" + "," + user_crops.WHEAT + " = " + "\'" + cropLs[user_crops.WHEAT] + "\'" + "," + user_crops.MUNG_BEAN + " = " + "\'" + cropLs[user_crops.MUNG_BEAN] + "\'" + "," + user_crops.TEA + " = " + "\'" + cropLs[user_crops.TEA] + "\'" + "," + user_crops.MILLET + " = " + "\'" + cropLs[user_crops.MILLET] + "\'" + "," + user_crops.MAIZE + " = " + "\'" + cropLs[user_crops.MAIZE] + "\'"  +   " where " + user_crops.USERNAME + "=" + "\'" + farmerUsername + "\'" + ";" 
    
    print(query)

    try:
        #execute query
        cur.execute(query) 
    
        #commit to the DB
        mysql.connection.commit()

        #close the connection
        cur.close()

        print("successfully updated crop list for the user")
        return ('201')
        
    except mysql.connection.Error as error:
        print("Error updating" + error)
        return ('500')

@app.route('/getSuggestedCrops')
def getSuggestedCrop():

    #current condition needs to be changed here
    currentCondition = {
        crop_properties.TEMPERATURE:"23-45",#degree celcius
        crop_properties.HUMIDITY:"40-80",#percentage
        crop_properties.RAINFALL:"120",
        "locationDensity":"4"#-((0.3x)^2)
    }

    cur = mysql.connection.cursor()

    query = "select * from " + crop_properties.TABLE_NAME + ";"

    cur.execute(query)
    rows = cur.fetchall()
    crop_prop = {}
    for row in rows:
        crop_prop[row[crop_properties.CROPNAME]] = row

    cur.close()

    crop_points = {}

    for x in CROPS:
        crop_points[x] = 0

    crop_points = MV.CalculatePoints(crop_points,crop_prop,currentCondition)
    print(crop_points)


    sorted_crop_points = sorted(crop_points.items(),key=lambda parameter_list: parameter_list[1])

    return str(sorted_crop_points)

if __name__ == '__main__':
    SESSION_ID = random.randint(1,1000)
    for i in range(0,len(getmembers(user_crops))-8):
        if(getmembers(user_crops)[i][0]!='TABLE_NAME' and getmembers(user_crops)[i][0]!='USERNAME'):
            print(getmembers(user_crops)[i][1])
            CROPS.insert(0,getmembers(user_crops)[i][1])
    app.run(host = '192.168.1.9',debug=True)
