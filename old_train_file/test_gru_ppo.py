# from env.minigrid import MiniGrid_fourroom_obs8x8
from pygame import FINGERDOWN
# from env.minigrid_neverdone import MiniGrid_fourroom_obs8x8
from env.minigrid_neverdone_perfect_reward import MiniGrid_fourroom_obs8x8

from env.find_ball import FindBall

# from pfc.gru_pred_conv_8x8 import GruPredHid
from pfc.gru_pfc_minigrid import PPO_GRU_Module
from myf_ML_util import timer_tool
from mlutils.ml import continue_to_discrete
from mlutils.ml import one_hot
import hyperparam as hp
import paddle
import numpy as np
import copy
# import logging
import time
"minigrid"
# def env_obs_to_paddle_vec(obs):
#     obs=paddle.to_tensor(np.reshape(obs,[1,1,-1]))
#     return obs
def env_obs_to_paddle_vec(obs):
    return paddle.to_tensor(np.reshape(np.array(obs,dtype=np.float32),[1,1,-1]))



def main():
    # logging.basicConfig(filename="log/"+time.strftime("%Y_%m%d_%H%M%S",time.localtime(time.time()))+".txt", level=logging.INFO)

    # env=MiniGrid_fourroom_obs8x8()
    env=FindBall()
    cd=continue_to_discrete(env.action_num,False,tanh_scale=6)
    # input_output_info={
    #     "game_name":"minigrid",
    #     'to_static':True,
    #     'train_batchsize':4,
    #     'env_vec_dim':8*8*3,
    #     'obs_dim':8*8*3,
    #     'action_env_dim':2,
    #     'action_dim':2,
    #     'actor_gru_hid_dim':256,
    #     'critic_gru_hid_dim':256
    #     }
    input_output_info={
        "game_name":"findball",
        'to_static':True,
        'train_batchsize':4,
        'env_vec_dim':env.obs_dim,
        'obs_dim':env.obs_dim,
        'action_env_dim':env.action_dim,
        'action_dim':env.action_dim,
        'actor_gru_hid_dim':256,
        'critic_gru_hid_dim':256
        }
    pfc_interact=PPO_GRU_Module(input_output_info)
    pfc_interact.model.eval() 


    input_output_info_train=copy.deepcopy(input_output_info)
    input_output_info_train['to_static']=False
    pfc_train=PPO_GRU_Module(input_output_info_train)
    pfc_train.load_model('all_models/pfc_model',180)
    

    "初始化"
    env_obs=env.reset()
    # kl_pred_net.pred_reset()
    # env_obs=np.reshape(np.transpose(env_obs,[2,0,1]).astype(np.float32),[-1])/255
    # input_dict=from_env_obs_to_input_dict(env_obs_dict,0)
    input_dict={
        "env_vec":env_obs_to_paddle_vec(env_obs)
    }
    pfc_interact._reset()
    pfc_train._reset()
    tt_main=timer_tool("train pfc",_debug=True)
    "初始化rpm第0步的obs"
    pfc_train.rpm.env_vec[0]=env_obs_to_paddle_vec(env_obs).numpy().reshape([-1])

    for e in range(10000000000000000000):
        ppo_reward=0
        env_ep_time=0
        pfc_ep_time=0
        bg_ep_time=0

        pfc_interact.update(pfc_train.model.state_dict())


        tt_main.start()
        # print("init c_h",np.mean(np.abs(pfc_interact.agent.alg.model.actor_model.h.numpy())))
        pfc_interact._reset()
        with paddle.no_grad():
            for j in range(hp.PPO_NUM_STEPS):
                t_j=timer_tool("j step",False)
                # tt.start()
                

                h_dict={
                    'actor_init_h':None,
                    'critic_init_h':None
                }
                

                
                """
                output_dict={
                    "value":np.squeeze(value),
                    "action":np.squeeze(action),
                    "action_log_prob":np.squeeze(action_log_prob),
                    "actor_gru_h1":actor_gru_h1,
                    "actor_gru_h2":actor_gru_h2,
                    "critic_gru_h":critic_gru_h
                }
                """
                # pfc_output_dict=pfc_interact._input(input_dict,train=False,h_dict=h_dict)
                # pfc_value,pfc_action,pfc_action_log_prob,pfc_actor_gru_h,pfc_critic_gru_h=[pfc_output_dict[key] for key in ['value','action','action_log_prob','actor_gru_h','critic_gru_h']]
                pfc_action=pfc_interact.agent.predict(input_dict,train=False,h_dict=h_dict)
                pfc_action=np.reshape(pfc_action,[-1])
                # print(np.mean(np.abs(pfc_critic_gru_h)))
                discrete_pfc_env_action=cd.to_discrete(pfc_action)
                # print(discrete_pfc_env_action)
                # print(pfc_action.shape)
                # input()
                # pfc_action_env=cd.to_discrece(np.tanh(pfc_action))

                # print(pfc_action)
                # pfc_action_hpc=(np.tanh(pfc_action[2:])+1)/2
                "inner reward"

                # print("env_action",pfc_action,one_hot(discrete_pfc_env_action,3))
                next_env_obs,reward,done,info=env.step(discrete_pfc_env_action)

                # print(next_env_obs,pfc_action,reward,env.ball_index_list)


                next_input_dict={"env_vec":env_obs_to_paddle_vec(next_env_obs)}
                t_j.end_and_start("env")


                ppo_reward+=info['out_reward']

                # print(np.mean(np.abs(pfc_train.rpm.actor_gru_h[0])))
                input_dict=next_input_dict
                t_j.end_and_start("collect")
                t_j.analyze()
            print(ppo_reward/hp.PPO_NUM_STEPS)
            
       



                
if __name__=="__main__":
    main()