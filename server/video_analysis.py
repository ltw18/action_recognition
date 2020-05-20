import cv2
import matplotlib.pyplot as plt
import sys
from actions_from_video import Action
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
    
