import cv2
import matplotlib.pyplot as plt
import sys
from actions_from_video import Action
import base64
from io import BytesIO
import numpy as np
# def open_video():
#     capture = cv2.VideoCapture(-1)
    # return 1
def analysis(file_path):
    s = Action()
    res = s.Offline_Analysis(file_path)
    suggestion = 1
    alarm_action = list(res.keys())
    alarm_date = list(res.values())
    return alarm_action,alarm_date,suggestion

def Online_Init():
    return Action(reg_frame=9)

def Online_Analysis(action_class, img):
    format, imgstr = img.split(';base64,')
    img = base64.b64decode(imgstr)
    nparr = np.fromstring(img, np.uint8)
    img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    
    # print(img)
    # cv2.imshow('URL2Image',img)

    res = action_class.Online_Analysis(img)
    # print('res', res)
    resstr = ''
    if res==[]:
        return 'ID: N/A Action: N/A Alarm_level: N/A'
    for pid, act, alarm in res:
        resstr += 'ID: '+str(pid)+' Action: '+act+' Alarm_leval: '+str(alarm)+'\n'

    return resstr
    
