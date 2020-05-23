import torch
from torch.autograd import Variable
import torch.nn.functional as F
import numpy as np
from collections import OrderedDict
from action_recognition.tgn import Model

class TGN(object):
    def __init__(self, size=(1920,1080), device=[0], 
            weights='/home/zhangruiwen/05skeleton/03code/01ltw18_demo/action_recognition/models/action/tcn_bone-79-150240.pt'):
        self.device = device
        self.weights = weights
        self.vsize = size
        self.load_model()

    def load_model(self):
        output_device = self.device[0] if type(self.device) is list else self.device
        self.output_device = output_device
        
        self.model = Model().cuda(output_device)

        weights = torch.load(self.weights)
        weights = OrderedDict([[k.split('module.')[-1],
                v.cuda(output_device)] for k, v in weights.items()])

        self.model.load_state_dict(weights)

        if type(self.device) is list:
            if len(self.device) > 1:
                self.model = nn.DataParallel(self.model,
                    device_ids=self.device, output_device=output_device)

    def predict(self, data):
        self.model.eval()
        with torch.no_grad():
            data = self.preprocess(data)
            data = Variable(data.float().cuda(self.output_device))
            output = self.model(data)
            if isinstance(output, tuple):
                output, l1 = output
            score, ind = torch.max(F.softmax(output.data,1), 1)
            score = score.cpu().numpy()[0]
            ind = ind.cpu().numpy()[0]
            return self.return_label(ind)+'  %.2f'%(score)

    def preprocess(self, data):#T V C
        T, V, C = data.shape
        tmp = np.zeros((1,3,150,V,2))
        tmp[0, 0, :T, :, 0] = data[...,0]/self.vsize[0]-0.5
        tmp[0, 1, :T, :, 0] = 0.5-data[...,1]/self.vsize[1]
        return torch.from_numpy(tmp)

    def return_label(self, ind):
        label = ['Run','Jump','Walk','Stand','Wave']
        return label[ind%5]

        
