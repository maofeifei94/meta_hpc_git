class svaepred_info():
    "train info"
    # len_warmup=128
    # len_max_history=512
    # len_pred=8
    # len_kl=256
    # interval_kl=8
    # interval_pred=8
    # train_batch_size=4
    len_warmup=128
    len_max_history=512
    
    len_pred=128
    interval_pred=8

    len_kl=128
    interval_kl=len_kl

    train_batch_size=4



    "input dim"
    gloinfo_gauss_dim=128
    state_vec_dim=128+1
    action_vec_dim=4

    "train param"
    train_lr=0.0001
    train_kl_loss_ratio=1e-8

    # gloinfo
    "input fc"
    gloinfo_ifc_input_dim=state_vec_dim+action_vec_dim
    gloinfo_ifc_mid_dim=128
    gloinfo_ifc_mid_layers=2
    gloinfo_ifc_output_dim=128
    "gru"
    gloinfo_gru_dim=128
    "gauss_fc"
    gloinfo_gfc_input_dim=gloinfo_gru_dim
    gloinfo_gfc_mid_dim=128
    gloinfo_gfc_mid_layers=4
    gloinfo_gfc_output_dim=gloinfo_gauss_dim*2

    # locinfo
    "input fc"
    locinfo_ifc_input_dim=state_vec_dim+action_vec_dim
    locinfo_ifc_mid_dim=128
    locinfo_ifc_mid_layers=4
    locinfo_ifc_output_dim=128
    "gru"
    locinfo_gru_dim=128

    #predfc
    "pred fc"
    Q_dim=64
    V_num=16  
    V_dim=128
    K_dim=Q_dim*V_num


    pred_Qnet_input_dim=locinfo_gru_dim
    pred_Qnet_mid_dim=128
    pred_Qnet_mid_layers=2
    pred_Qnet_output_dim=Q_dim

    pred_Knet_input_dim=gloinfo_gauss_dim
    pred_Knet_mid_dim=128
    pred_Knet_mid_layers=2
    pred_Knet_output_dim=K_dim

    pred_Vnet_input_dim=gloinfo_gauss_dim
    pred_Vnet_mid_dim=128
    pred_Vnet_mid_layers=2
    pred_Vnet_output_dim=V_dim*V_num

    pred_fc_input_dim=V_dim+locinfo_gru_dim
    pred_fc_mid_dim=128
    pred_fc_mid_layers=4
    pred_fc_output_dim=state_vec_dim



    