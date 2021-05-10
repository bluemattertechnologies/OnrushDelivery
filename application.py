from dateutil import parser
from flask import Flask, request, jsonify,render_template,redirect,url_for,send_file,session,g,Response
from flask_socketio import SocketIO, send, join_room, leave_room, emit
from werkzeug.utils import secure_filename
from datetime import date,datetime,time,timedelta
import sqlite3
import json
import re

app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static')
app.config["upload_folder"] = 'web/static/images/'
app.config["upload_folder2"] = 'web/static/'

app.config['SECRET_KEY']='mysecret'
socketio = SocketIO(app, cors_allowed_origins="*")


@app.route('/')
def index():
    return ("Hello WOrld")

@app.route("/validate_cus", methods=['GET','POST'])                 
def validate_cus():
    data=request.json
    query = "INSERT INTO CUSTOMER_AUTH VALUES('%s','%s')"%(data['cus_ph'],data['user_id'])
    if inUP(query):
        response={
            'status':200,
            'type':'new'
        }
    else:
        query = "UPDATE CUSTOMER_AUTH SET user_id='%s' WHERE cus_ph='%s'"%(data['user_id'],data['cus_ph'])
        if inUP(query):
            return userdetails(data['cus_ph'])
        else:
            response={
            'status':404
            }
    return response


@app.route("/add_cusinfo", methods=['GET','POST'])                 
def add_cusinfo():
    data=request.json
    if(data['status']=='new'):
        query = "INSERT INTO CUSTOMER(cus_ph,cus_name,cus_email) VALUES('%s','%s','%s')"%(data['cus_ph'],data['cus_name'],data['cus_email'])
    if(data['status']=='update'):
        query = "UPDATE CUSTOMER SET (cus_name,cus_email)=('%s','%s') WHERE cus_ph='%s'"%(data['cus_name'],data['cus_email'],data['cus_ph'])
    if inUP(query):
        return userdetails(data['cus_ph'])
    else:
        response={
            'status':404
        }


def userdetails(cus_ph):
    query = "SELECT * FROM CUSTOMER WHERE cus_ph ='%s'"%(cus_ph)
    data=selection(query)
    response={
        'status':200,
        'type':'new'
    }
    if data!=False:
        for d in data:
            response={
                'status':200,
                'type':'existing',
                'cus_id':d[0],
                'cus_ph':d[1],
                'cus_name':d[2],
                'cus_mail':d[3],
            }
    return response
   

@app.route("/get_category", methods=['GET','POST'])                 
def get_category():
    query = "SELECT * FROM PRODUCT_TYPE ORDER BY type_order"
    data=selection(query)
    if data!=False:
        item=[]
        for d in data:
            x={
                'pro_type':d[0],
                'type_order':d[1]
            }
            item.append(x)
        response={
            'status':200,
            'list':item
        }
    else:
        response={
            'status':404
        }
    return response
     

@app.route("/get_popularprod", methods=['GET','POST'])                 
def get_popularprod():
    response={
        'status':404
    }
    data=request.json
    query = "SELECT pro_type FROM PRODUCT_TYPE WHERE type_order='%s'"%(data['type_order'])
    detail=selection(query)
    if detail!=False:
        item=[]
        for d in detail:
            query = "SELECT * FROM PRODUCT WHERE pro_type='%s' AND pro_status='1' ORDER BY pro_score LIMIT 10"%(d[0])
            detail2=selection(query)
            if detail2!=False:
                for a in detail2:
                    x={
                        'pro_id':a[0],
                        'ven_id':a[0],
                        'ven_name':a[2],
                        'pro_name':a[4],
                        'pro_price':a[5],
                        'pro_score':a[8]                    
                    }
                    item.append(x)
                response={
                    'status':200,
                    'list':item
                }    
    return response


@app.route("/get_searchprodlist", methods=['GET','POST'])                 
def get_searchprodlist():
    response={
        'status':404
    }
    keyword=request.json['text']
    item=[]
    query = "SELECT pro_name,pro_type,pro_score FROM PRODUCT WHERE pro_name  LIKE '%s'"%("%"+keyword+"%")
    detail=selection(query)
    if detail!=False:
        for d in detail:
            response={
                'text':d[0],
                'type':d[1],
                'score':d[2]
            }
            item.append(response)
    query = "SELECT pro_type,pro_typeScore FROM PRODUCT_TYPE WHERE pro_type LIKE '%s'"%("%"+keyword+"%")
    detail=selection(query)
    if detail!=False:
        for d in detail:
            response={
                'text':d[0],
                'type':"Category",
                'score':d[1]
            }
            item.append(response)
    query = "SELECT ven_name,ven_score FROM VENDOR WHERE ven_name LIKE '%s'"%("%"+keyword+"%")
    detail=selection(query)
    if detail!=False:
        for d in detail:
            response={
                'text':d[0],
                'type':"Shop",
                'score':d[1]
            }
            item.append(response)
    
    data=[]
    for a in item:
        if select_prod(a['text'],keyword):
            data.append(a)
        # data = sorted(data, key=lambda k: k.get['score']', 0), reverse=True)
        response={
            "status":200,
            "data":data
        }
    return response





def select_prod(word,keys):
    s=word.split(" ")
    for x in s:
        if x.lower().startswith(str(keys).lower()):
            return True


###################### DATABASE ###################################
def inUP(query): #Insertion or Updation Queries
    try:
        connection = sqlite3.connect('onRush.db')       
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False
def selection(query):  #Selection Queries
    try:
        connection = sqlite3.connect('onRush.db')       # Connect to the database
        connection.row_factory = sqlite3.Row
        cursor =  connection.cursor()
        cursor.execute(query)
        connection.commit()
        rv = cursor.fetchall()
        connection.close()
        return rv
    except Exception as e:
        print(e)
        return False
###################### DATABASE ###################################


# if __name__ == '__main__':
#     # socketio.run(app,host='0.0.0.0',port=5000)
#     app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT',8080)))

