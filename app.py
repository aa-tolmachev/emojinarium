from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
import traceback
from xml.etree import ElementTree as ET


#import self libs
import test.test_get_message as t_gm
from models import main as models_main





application = Flask(__name__)  # Change assignment here

#test
@application.route("/")  
def hello():
    resp = "Hello World!"
    return resp


#get message from messanger and calc messages models
@application.route('/get_message', methods=['GET', 'POST'])  
def get_message():
    response = {'status' : 'ok',
                'code' : 200,
                'message_id' : None,
                'dialog_id' : None,
                'participants_id' : None,
                'user_id' : None,
                'models' :[]
               }
    try:
        getData = request.get_data()
        json_params = json.loads(getData) 
        

        #json_params = {'message_id':0,
        #                'dialog_id':0,
        #                'participants_id':0,
        #                'user_id':0,
        #                'content':'test content',
        #                'created_at':111111111,
        #            }



        response['message_id'] = json_params['message_id']
        response['dialog_id'] = json_params['dialog_id']
        response['participants_id'] = json_params['participants_id']
        response['user_id'] = json_params['user_id']


        #make test models predict (for message , model_id = 0)
        #model_resp = t_gm.make_random_model(json_params = json_params , model_id = 0, model_to = 'message_id')
        #response['models'].append(model_resp)
        
        #make real emoji predict for message
        response['models'] = models_main.main(json_params = json_params , model_to = 'message_id')

        
        
    except:
        traceback.print_exc()
        response['status'] = 'error'
        response['code'] = 501


    response = json.dumps(response)
    print(response)
    return str(response)
        


if __name__ == "__main__":
    #heroku
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0' , threaded=True)
    #local
    #application.run()