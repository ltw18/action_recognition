import os
import sys
import numpy as np
import cv2
import time
sys.path.append('../')
from object_track.track import Sort
from action_recognition.recognition import TGN
from op_python.openpose import pyopenpose as op

class Action(object):
    def __init__(self, max_age=8, min_hits=1, reg_frame=10):
        params = dict()
        params["model_folder"] = "../models"
        params['prototxt_path']='pose/coco/pose_deploy_linevec.prototxt'
        params['caffemodel_path'] = 'pose/coco/pose_iter_440000.caffemodel'
        params['model_pose'] = 'COCO'
        alarm_action = ['Jump', 'Run']
        self.opWrapper = op.WrapperPython()
        self.opWrapper.configure(params)
        self.opWrapper.start()
        self.datum = op.Datum()
        self.mot_tracker = Sort(max_age, min_hits)
        self.act_reg     = TGN()
        self.reg_frame = reg_frame
        self.result = {}
        for k in alarm_action:
            self.result[k] = []
        self.skeleton_sequence = {}

    def Filter_valid_pionts(self, keyPoints, valid_num=11):
        if len(keyPoints.shape)<2:
            return None, 0, 0
        validpoints=[]
        for i, p in enumerate(keyPoints[...,:2]):
            if p[1,1]>0 and p[8,1]+p[11,1]>0 and p[10,1]+p[13,1]>0:
                if len(set(np.where(p>0)[0])) >valid_num:
                    validpoints.append(p)
        # print('People num:', num_people, '| valid num:', valid_people)
        return np.array(validpoints), len(validpoints), keyPoints.shape[0]

    def Get_bbox(self, data):
        def Get_Bounding_Box(skeleton_data, xmax=1910, ymax=1070, xp=0.2, yp=0.12): #n*18*2
            ind = np.where(skeleton_data>0)[0]
            skeleton_data = skeleton_data[ind]
            x1,y1 = min(skeleton_data[:,0]), min(skeleton_data[:,1])
            x2,y2 = max(skeleton_data[:,0]), max(skeleton_data[:,1])
            x1 = max(0,    x1-int((x2-x1)*xp)) 
            x2 = min(xmax, x2+int((x2-x1)*xp)) 
            y1 = max(0,    y1-int((y2-y1)*yp)) 
            y2 = min(ymax, y2+int((y2-y1)*yp)) 
            # 500case, y/x: mean:2.67, test:0.87 
            if (y2-y1)/(x2-x1)>3.5:
                x1 = max(0,    (x2+x1)//2-(y2-y1)/2/2.67)
                x2 = min(xmax, (x2+x1)//2+(y2-y1)/2/2.67)
            elif (y2-y1)/(x2-x1)<1.6:
                y1 = max(0,    (y1+y2)//2-(x2-x1)/2*2.67) 
                y2 = min(ymax, (y1+y2)//2+(x2-x1)/2*2.67) 
            return np.array([x1,y1,x2,y2])

        bbox = np.zeros((data.shape[0], 4), dtype=np.int)
        for i, v in enumerate(data):
            bbox[i] = Get_Bounding_Box(v)
        return bbox

    def Put_Text_Rec(self, o_id, box, act, j, img):
        cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0,0,255), 2)
        word = 'ID: '+str(o_id)
        cv2.putText(img, word, (box[0], box[1]-5), cv2.FONT_HERSHEY_COMPLEX, 1, (20,10,250),3)
        cv2.putText(img, word+' Act: '+str(act), (50, 300+j*50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0,0,250), 3)

    def Offline_Analysis(self, video_path, video_save=None, image_save=None, step=6):
        frame_cnt = 0
        cap = cv2.VideoCapture(video_path)
        fps, size = int(cap.get(cv2.CAP_PROP_FPS)), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                                     int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.act_reg.vsize = size
        self.fps = fps
        step = fps//5
        # print(fps)
        if video_save:
            os.makedirs(video_save, exist_ok=True)
            video_writer=cv2.VideoWriter(video_save, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, size)
        b = time.time()
        ret=True
        while cap.isOpened() and ret==True:
            frame_cnt += 1
            ret, frame = cap.read()
            if not ret: break
            if frame_cnt%step!=0: continue
            # print(ret, type(frame))
            self.datum.cvInputData = frame
            self.opWrapper.emplaceAndPop([self.datum])
            keyPoints = self.datum.poseKeypoints
            if image_save or video_save:
                resPic = self.datum.cvOutputData
                cv2.putText(resPic, 'Frame: '+str(frame_cnt), (50, 230), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 225,234),4)
            
            validpoints, num_p, all_p = self.Filter_valid_pionts(keyPoints)
            # print('\n------- Frame:', frame_cnt,'| Valid num:', num_p, '| People num:', all_p, '--------')
            if num_p==0: continue
            bbox = self.Get_bbox(validpoints)
            IDs = self.mot_tracker.update(bbox).astype(np.int)
            for j, (x1,y1,x2,y2,o_id) in enumerate(IDs):
                if o_id in self.skeleton_sequence.keys():
                    self.skeleton_sequence[o_id].append(validpoints[j])
                else:
                    self.skeleton_sequence[o_id] = [validpoints[j]]

                if len(self.skeleton_sequence[o_id])==self.reg_frame:
                    res = self.act_reg.predict(np.array(self.skeleton_sequence[o_id]))
                    self.skeleton_sequence[o_id].pop(0)
                    self.result = self.alarm(res, frame_cnt)
                else:
                    res = 'None'
                if image_save or video_save:
                    Put_Text_Rec(o_id, (x1,y1,x2,y2), res, j, resPic)
            if image_save:
                os.makedirs(os.path.join(image_save, str((frame_cnt-1)//100)), exist_ok=True)
                cv2.imwrite(os.path.join(image_save, str((frame_cnt-1)//100), str(frame_cnt)+'.jpg'), resPic)
            if video_save:
                video_writer.write(resPic)
        print(time.time()-b)
        return self.result

    def alarm(self, res, frame_cnt=-1, threshold=5):
        def alarm_level(action):
            return 1
        act = res.split()[0]
        if frame_cnt<0: 
            return alarm_level(act)
        if act in self.result.keys():
            second = round(frame_cnt/self.fps)
            if self.result[act]:
                if second-self.result[act][-1]>threshold:
                    self.result[act].append(second)
            else:
                self.result[act] = [second]
        return self.result

    def Online_Analysis(self, image, video_save=None, image_save=None):
        result = []
        self.datum.cvInputData = image
        self.opWrapper.emplaceAndPop([self.datum])
        keyPoints = self.datum.poseKeypoints
            
        validpoints, num_p, all_p = self.Filter_valid_pionts(keyPoints)
        
        # print('\n------- Frame:', frame_cnt,'| Valid num:', num_p, '| People num:', all_p, '--------')
        if num_p==0: return result
        bbox = self.Get_bbox(validpoints)
        # print(bbox)
        IDs = self.mot_tracker.update(bbox).astype(np.int)
        res='no'
        for j, (x1,y1,x2,y2,o_id) in enumerate(IDs):
            if o_id in self.skeleton_sequence.keys():
                self.skeleton_sequence[o_id].append(validpoints[j])
            else:
                self.skeleton_sequence[o_id] = [validpoints[j]]
            print(len(self.skeleton_sequence[o_id]), self.reg_frame)
            if len(self.skeleton_sequence[o_id])>=self.reg_frame:
                res = self.act_reg.predict(np.array(self.skeleton_sequence[o_id]))
                self.skeleton_sequence[o_id].pop(0)
                result.append((o_id, res, self.alarm(res)))
                print(IDs, res)
        # print('NUM',num_p, IDs, res)
        return result

if __name__ == '__main__':
    s = Action()
    s.recognition("/data/zhangruiwen/openpose/05video/video.mp4")
