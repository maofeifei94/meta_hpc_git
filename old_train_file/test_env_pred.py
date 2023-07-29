

import numpy as np
import cv2
import time
from multiprocessing import Process,Queue,Pipe
import threading
from mlutils.ml import one_hot
from mlutils.data import npy_compress
import random
import os
class npy_data_reader():
    def __init__(self) -> None:
        self.data_dir="all_data/minigrid_history"
        self.nc=npy_compress()
        self.reset()
    def reset(self):
        self.current_index=0
        self.npy_num_list=self.get_all_npy_zip_num(self.data_dir)
        self.npy_file_num=len(self.npy_num_list)
        
        random.shuffle(self.npy_num_list)
        print(f"start new npy loop with file name {self.npy_file_num}")
        # print(self.npy_num_list)
        # print("npy start new loop with data num ",self.npy_num)
        # print(os.listdir(self.data_dir))
    def get_all_npy_zip_num(self,data_dir):
        num_list=[]
        for f in os.listdir(data_dir):
            if f[-8:]==".npy.zip":
                num=int(f[:-8])
                num_list.append(num)
        return num_list

    def get_data(self):
        current_npy_name=f"{self.npy_num_list[self.current_index]}.npy"

        current_npy_path=f"{self.data_dir}/{current_npy_name}"

        current_zip_name=f"{current_npy_name}.zip"

        current_zip_path=f"{self.data_dir}/{current_zip_name}"

        # print("decompress")
        self.nc.decompress(current_zip_path,self.data_dir,current_npy_name)
        current_data=np.load(current_npy_path,allow_pickle=True).item()
        self.nc.delete_f(current_npy_path)
        self.current_index+=1
        if self.current_index>=self.npy_file_num:
            self.reset()
        return current_data
def render_pred(label,pred):
    ratio=50
    cv2.imshow("label",cv2.resize(label,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA))
    cv2.imshow("pred",cv2.resize(pred,None,fx=ratio,fy=ratio,interpolation=cv2.INTER_AREA))
    cv2.waitKey(100)
def render_history(s_history,pred_history,render_img_list,kl_list):
    for i in range(len(s_history)):
        label_img=np.transpose(s_history[i],[1,2,0])
        pred_img=(np.transpose(pred_history[i],[1,2,0])*255).astype(np.uint8)
        render_img=render_img_list[i]
        kl=kl_list[i]
        cv2.putText(render_img,f"{i},{str(round(kl,3))}",(0,20),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
        cv2.imshow("label",cv2.resize(label_img,None,fx=5,fy=5,interpolation=cv2.INTER_AREA))
        cv2.imshow("pred",cv2.resize(pred_img,None,fx=5,fy=5,interpolation=cv2.INTER_AREA))
        cv2.imshow("render",render_img)
        cv2.waitKey()

def test():
    from mlutils.ml import moving_avg
    from pfc.gru_pred_conv import GruPredHid 
    from vae.minigrid_vae import MinigridVae
    from env.minigrid import MiniGrid_fourroom
    prednet=GruPredHid()
    env=MiniGrid_fourroom()
    prednet.load_model("all_models/minigrid_model",180000)

    vae_net=MinigridVae()
    vae_net.load_model("all_models/minigrid_vae_model",36000)

    # #npy_read
    # ndr=npy_data_reader()
    # data=ndr.get_data()
    # obs_feature_history=data["obs_feature_history"]
    # action_history=data["action_history"].astype(np.float32)
    # action_history=np.concatenate([action_history]*3,axis=-1)
    # print(obs_feature_history.shape,action_history.shape)

    # for i in range(1000):
    #     pred_img,kl_loss=prednet.test(obs_feature_history[i:i+1],action_history[i:i+1],vae_net)

    #env_collect
    while 1:
        obs=env.reset()
        done=False
        a_history=[]
        s_history=[]
        render_img_list=[]
        env_time=time.time()
        while not done:
            action=np.clip(np.random.randint(0,4),0,2)
            ball_obs=obs
            s_history.append(np.transpose(ball_obs,[2,0,1]))
            a_history.append([action])
            obs,reward,done=env.step(action)
            render_img=env.render(show=False)
            render_img_list.append(render_img)
        "预测"
        action_history=np.array([a_history],dtype=np.int)
        one_hot_action=np.concatenate([action_history]*3,axis=-1).astype(np.float32)
        obs_feature_history=vae_net.pred(np.array(s_history))

        pred_img,kl_loss=prednet.test([obs_feature_history],one_hot_action,vae_net)

        "history添加最后一步"
        s_history.append(np.transpose(obs,[2,0,1]))
        s_history=s_history[1:]

        render_history(s_history,pred_img[0],render_img_list,np.log10(kl_loss[0]))
    




if __name__=="__main__":
    # train_pred()
    test()
