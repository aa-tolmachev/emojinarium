from flask import Flask
from flask import request
import requests
from flask import make_response
import os
import json
import traceback
from xml.etree import ElementTree as ET
import string
import random


#import self libs
import test.test_get_message as t_gm
from models import main as models_main


import logging
#import timber

log_apikey = os.getenv('timber_apikey')
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

#timber_handler = timber.TimberHandler(source_id='14767', api_key=log_apikey)
#logger.addHandler(timber_handler)


application = Flask(__name__)  # Change assignment here




#define loger func
def log(logger, json_params=None,step='new',internal_id=None):
    if json_params is None:
        logger.info('internal_id:{0} , step:{1}'.format(internal_id,step))
    elif 'message_id' not in json_params.keys():
        logger.info('internal_id:{0} , step:{1} '.format(internal_id,step), extra={
          'json_params': json_params
        })
    else:
        logger.info('internal_id:{0} , step:{1} , message_id{2}'.format(internal_id,step,json_params['message_id']), extra={
          'json_params': json_params
        })
#create random string
def randomString(stringLength=10):
    """Generate a random string of fixed length """
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(stringLength))

#test
@application.route("/")  
def hello():
    resp = "Hello World!"
    return resp


#get message from messanger and calc messages models
"""
input example
{"message_id":0,
    "dialog_id":0,
    "participants_id":0,
    "user_id":0,
    "content":"Блять, как ты надоел. Реально у вас ничего не работает!!!",
    "created_at":111111111
}

output example
{"status": "ok", 
    "code": 200, 
    "message_id": 0, 
    "dialog_id": 0, 
    "participants_id": 0, 
    "user_id": 0, 
    "models":
        [{"model_id": 1, 
            "model_score": -1, 
            "model_probe": 0.81, 
            "model_to": "message_id", 
            "to_id": 0
            }
        ]
}

"""
@application.route('/get_message', methods=['GET', 'POST'])  
def get_message():
    internal_id = randomString(10)
    status_code = 200
    
    response = {'status' : 'ok',
                'code' : 200,
                'message_id' : None,
                'dialog_id' : None,
                'participants_id' : None,
                'user_id' : None,
                'models' :[]
               }
    
    try:

        log(logger,step='new',internal_id=internal_id)
        getData = request.get_data()
        json_params = json.loads(getData) 
        print(json_params)
        log(logger,json_params,'get json_params',internal_id)
        #json_params = {'message_id':0,
        #                'dialog_id':0,
        #                'participants_id':0,
        #                'user_id':0,
        #                'content':'test content',
        #                'created_at':111111111,
        #            }


        status_code = 400
        response['message_id'] = json_params['message_id']
        response['dialog_id'] = json_params['dialog_id']
        response['participants_id'] = json_params['participants_id']
        response['user_id'] = json_params['user_id']


        #make test models predict (for message , model_id = 0)
        #model_resp = t_gm.make_random_model(json_params = json_params , model_id = 0, model_to = 'message_id')
        #response['models'].append(model_resp)
        
        #make real emoji predict for message
        status_code = 500
        response['models'] = models_main.main(json_params = json_params , model_to = 'message_id')
        log(logger,json_params,'model done',internal_id)
        
        status_code = 200
        
        
    except:
        if status_code == 200:
            status_code = 500
        traceback.print_exc()
        response['status'] = 'error'
        response['code'] = 501
        log(logger,json_params,'some error',internal_id)


    response = json.dumps(response, ensure_ascii=False)
    print(response)
    return str(response)  , status_code
        


"""
input example
{"dialog_id":0,
    "user_id":0,
    "content":"Александр Толмачёв, [27.02.2023 13:07]\nтак и для тестов и для восприятия и для использования огонь будет\n\nЕвгений Султан, [27.02.2023 13:09]\nДа, мне тоже гуд. Весь лк пока в драфтовом состоянии, сейчас на реальных данных сделаем пушку-интерфейс\n\nСергей Савин Ozon, [27.02.2023 13:10]\nкстати\n\nСергей Савин Ozon, [27.02.2023 13:10]\nстраницу авторизации надо на русский перевести",
    "created_at":111111111
}

output example
{"status": "ok", 
    "code": 200, 
    "dialog_id": 0, 
    "user_id": 0, 
    "dialog":
        [{"message":{"user_name" : "Александр Толмачёв",
                    "created_dt" : "27.02.2023 13:07",
                    "text" : "так и для тестов и для восприятия и для использования огонь будет",
                    },
            "models":
                [{"model_id": 1, 
                    "model_score": -1, 
                    "model_probe": 0.81
                    }
                ]
        },...
        ]
}

"""
@application.route('/get_dialog', methods=['GET', 'POST'])  
def get_dialog():
    internal_id = randomString(10)
    status_code = 200
    
    response = {'status' : 'ok',
                'code' : 200,
                'dialog_id' : None,
                'user_id' : None,
                'dialog' :[]
               }
    
    try:

        log(logger,step='new',internal_id=internal_id)
        getData = request.get_data()
        json_params = json.loads(getData) 
        print(json_params)
        log(logger,json_params,'get json_params',internal_id)


        status_code = 400
        response['dialog_id'] = json_params['dialog_id']
        response['user_id'] = json_params['user_id']


        
        #make real emoji predict for message
        status_code = 500
        response['dialog'] = models_main.main_dialog(json_params = json_params , model_to = 'dialog_id')
        log(logger,json_params,'model done',internal_id)
        
        status_code = 200
        
    except:
        if status_code == 200:
            status_code = 500
        traceback.print_exc()
        response['status'] = 'error'
        response['code'] = 501
        log(logger,json_params,'some error',internal_id)


    response = json.dumps(response, ensure_ascii=False)
    print(response)
    return str(response)  , status_code



if __name__ == "__main__":
    #heroku
    port = int(os.getenv('PORT', 5000))
    application.run(debug=False, port=port, host='0.0.0.0' , threaded=True)
    #local
    #application.run()