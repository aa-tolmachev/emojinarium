
import pandas as pd
import re
import numpy as np
import pickle
import requests


import fasttext
global model
model = fasttext.load_model("./models/model.bin")


#from sklearn import linear_model
#from sklearn.linear_model import SGDClassifier as SGD

import os
token = os.getenv('deepai_token')

filename = './models_pkl/gba2fs.pkl'
#model_0 = pickle.load(open(filename, 'rb'))

def fasttext_predict(text_message):
    fst_result = {'sentiment' : 0
                 ,'proba' : 0}
    
    global model
    
    
    m_predict = model.predict(text_message)
    sentiment = m_predict[0][0]
    if sentiment == '__label__neutral':
        fst_result['sentiment'] = 0
    elif sentiment == '__label__negative':
        fst_result['sentiment'] = -1
    elif sentiment == '__label__positive':
        fst_result['sentiment'] = 1
    fst_result['proba'] = m_predict[1][0]
    
    
    
    
    return fst_result



def main(text_message = 'test' , model_to = 'message_id' , to_id = 0):

    dialog = []

    #preprocess data
    text_message = text_message.replace('\\n','\n')

    messages = text_message.split('\n\n')

    for m , i in zip( messages , range(len(messages)) ):
        
        re_match = re.match(r"^(.*), \[(.*)\]\n(.*)$", m)
        
        if re_match:
            messages[i] = (re_match[1] , re_match[2] , re_match[3])
        else:
            messages[i] = (None , None , m)
            
    df_chat = pd.DataFrame(messages)
    df_chat.columns = ['user_name' , 'created_dt' , 'text']


    df_chat.dropna(inplace = True)

    df_chat = df_chat.sort_values(by = ['created_dt'] , ascending = True)
    df_chat.reset_index(drop = True , inplace = True)


    #predict
    df_chat['positive'] = 0
    df_chat['neutural'] = 0
    df_chat['negative'] = 0

    df_chat['model_score'] = 0
    df_chat['model_probe'] = 0
    df_chat['model_id'] = 1


    for i , row in df_chat.iterrows():
        text_message = row['text']
        if not text_message:
            continue

        ft_result = fasttext_predict(text_message)
        if ft_result['sentiment'] == 0:
            df_chat.loc[ i , 'neutural'] = np.round(ft_result['proba'],2)
        elif ft_result['sentiment'] == -1:
            df_chat.loc[ i , 'negative'] = np.round(ft_result['proba'],2)
        elif ft_result['sentiment'] == 1:
            df_chat.loc[ i , 'positive'] = np.round(ft_result['proba'],2)
            
            
        #for prod
        df_chat.loc[i , 'model_score'] = ft_result['sentiment']
        df_chat.loc[i , 'model_probe'] = np.round(ft_result['proba'],2)


    #results
    df_message_results = df_chat[['user_name' , 'created_dt' , 'text']][:]
    message_arr = list(df_message_results.T.to_dict().values())

    df_model_results = df_chat[['model_id' , 'model_score' , 'model_probe']][:]
    models_arr = list(df_model_results.T.to_dict().values())


    for mes , mod1 in zip(message_arr , models_arr):
        dialog.append({'message':mes
                      ,'models':[{"model_id": int(mod1['model_id']),
                                 "model_score": int(mod1['model_score']),
                                 "model_probe":mod1['model_probe']}]})




    return dialog