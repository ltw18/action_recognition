import os
import sys
from sys import platform
import time
import argparse
import numpy as np
import cv2
from scipy.optimize import linear_sum_assignment
from object_track.track import Sort
from action_recognition.recognition import TGN

try:
    # Windows Import
    if platform == "win32":
        dir_path = os.path.dirname(os.path.realpath(__file__))
        sys.path.append(dir_path + '/../../python/openpose/Release');
        os.environ['PATH']  = os.environ['PATH'] + ';' + dir_path + '/../../x64/Release;' +  dir_path + '/../../bin;'
        import pyopenpose as op
    else:           
        # Change these variables to point to the correct folder (Release/x64 etc.)
        sys.path.append('./op_python')
        from openpose import pyopenpose as op
except ImportError as e:
    print('Error: OpenPose library could not be found. Did you enable `BUILD_PYTHON` in CMake and have this Python script in the right folder?')
    raise e


def Filter_valid_pionts(keyPoints, valid_num=11):
    if len(keyPoints.shape)<2:
        return None, 0, 0
    validpoints=[]
    for i, p in enumerate(keyPoints[...,:2]):
        if p[1,1]>0 and p[8,1]+p[11,1]>0 and p[10,1]+p[13,1]>0:
            if len(set(np.where(p>0)[0])) >valid_num:
                validpoints.append(p)
    # print('People num:', num_people, '| valid num:', valid_people)
    return np.array(validpoints), len(validpoints), keyPoints.shape[0]

def Get_bbox(data):
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

def Put_Text_Rec(o_id, box, act, j, img):
    cv2.rectangle(img, (box[0], box[1]), (box[2], box[3]), (0,0,255), 2)
    word = 'ID: '+str(o_id)
    cv2.putText(img, word, (box[0], box[1]-5), cv2.FONT_HERSHEY_COMPLEX, 1, (20,10,250),3)
    cv2.putText(img, word+' Act: '+str(act), (50, 300+j*50), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0,0,250), 3)

def main(op_params, video_path, video_out, img_out, reg_frame=10):
    # Starting OpenPose
    opWrapper = op.WrapperPython()
    opWrapper.configure(op_params)
    opWrapper.start()
    datum = op.Datum()
    cap = cv2.VideoCapture(video_path)
    fps, size = int(cap.get(cv2.CAP_PROP_FPS)), (int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), 
                                                 int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)))
    video_writer=cv2.VideoWriter(video_out, cv2.VideoWriter_fourcc('X', 'V', 'I', 'D'), fps, size)
    print('\n------------ Start -----------', fps, 'fps', size[0],'*', size[1],'-----------------------\n')
    
    mot_tracker = Sort(max_age=8,min_hits=1)
    act_reg     = TGN(size)
    skeleton_sequence = {}
    frame_cnt = 0
    b = time.time()
    while cap.isOpened() and frame_cnt<500:
        frame_cnt += 1
        ret, frame = cap.read()
        datum.cvInputData = frame
        opWrapper.emplaceAndPop([datum])
        resPic    = datum.cvOutputData
        keyPoints = datum.poseKeypoints
        cv2.putText(resPic, 'Frame: '+str(frame_cnt), (50, 230), cv2.FONT_HERSHEY_COMPLEX, 1.5, (0, 225,234),4)
        
        validpoints, num_p, all_p = Filter_valid_pionts(keyPoints)
        # print('\n------- Frame:', frame_cnt,'| Valid num:', num_p, '| People num:', all_p, '--------')
        if num_p>0:
            bbox = Get_bbox(validpoints)
            IDs = mot_tracker.update(bbox).astype(np.int)
            # print(IDs)
            for j, (x1,y1,x2,y2,o_id) in enumerate(IDs):
                if o_id in skeleton_sequence.keys():
                    skeleton_sequence[o_id].append(validpoints[j])
                else:
                    skeleton_sequence[o_id] = [validpoints[j]]

                if len(skeleton_sequence[o_id])==reg_frame:
                    res = act_reg.predict(np.array(skeleton_sequence[o_id]))
                    skeleton_sequence[o_id].pop(0)
                else:
                    res = 'None'
                Put_Text_Rec(o_id, (x1,y1,x2,y2), res, j, resPic)

        os.makedirs(os.path.join(img_out, str((frame_cnt-1)//100)), exist_ok=True)
        cv2.imwrite(os.path.join(img_out, str((frame_cnt-1)//100), str(frame_cnt)+'.jpg'), resPic)
        video_writer.write(resPic)
    print((time.time()-b)/500)
    


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--video_path", default="/data/zhangruiwen/openpose/05video/video.mp4")
    parser.add_argument("--video_out", default="./output/new_video.avi")
    parser.add_argument("--image_out", default="./output")
    args = parser.parse_known_args()
    # Custom Params (refer to include/openpose/flags.hpp for more parameters)
    params = dict()
    params["model_folder"] = "models"
    params['prototxt_path']='pose/coco/pose_deploy_linevec.prototxt'
    params['caffemodel_path'] = 'pose/coco/pose_iter_440000.caffemodel'
    params['model_pose'] = 'COCO'
    # Add others in path?
    for i in range(0, len(args[1])):
        curr_item = args[1][i]
        if i != len(args[1])-1: next_item = args[1][i+1]
        else: next_item = "1"
        if "--" in curr_item and "--" in next_item:
            key = curr_item.replace('-','')
            if key not in params:  params[key] = "1"
        elif "--" in curr_item and "--" not in next_item:
            key = curr_item.replace('-','')
            if key not in params: params[key] = next_item
    
    os.makedirs(args[0].image_out, exist_ok=True)

    main(params, args[0].video_path, args[0].video_out, args[0].image_out)
   