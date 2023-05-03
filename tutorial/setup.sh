#!/bin/bash

#=========================================
#
# Title: setup.sh
# Author: Andrew Naylor
# Date: Feb 23
# Brief: Setup nersc_cluster_deploy examples
#
#=========================================

## Parse Args
usage() {
  echo "Usage: $0 <Exercise Number>" 1>&2
}

exit_abnormal() {
  usage
  exit 1
}

if [ $# -lt 1 ]; then
    echo "Error: script requires exercise number"
    exit_abnormal
fi

setup_env() {
  ML_MODULE=$1
  module load $ML_MODULE
  echo "<> Setting up $ML_MODULE env"

  if python -m pip freeze | grep -q nersc-cluster-deploy
    then
      echo "<!> nersc_cluster_deploy is already setup..."
      return
  fi

  echo "<> Install nersc_cluster_deploy"
  python -m pip install git+https://github.com/asnaylor/nersc_cluster_deploy.git

  echo "<> Install Ray"
  python -m pip install ray[air]==2.3.0
}

setup_shifter_kernel(){
    IMAGE_NAME=$1
    CUSTOM_PYTHON_BIN=$2
    JUPYTER_KERNEL=$(echo $IMAGE_NAME | sed -r 's#[/:]+#_#g')
    JUPYTER_KERNEL_FOLDER=$HOME/.local/share/jupyter/kernels/$JUPYTER_KERNEL/
    CUSTOM_PYTHONUSERBASE=$HOME/.local/perlmutter/$JUPYTER_KERNEL

    ## Copy files across
    mkdir -p $JUPYTER_KERNEL_FOLDER
    cp .kernel.json $JUPYTER_KERNEL_FOLDER/kernel.json
    sed -i -e "s#CUSTOM_KERNEL_NAME#$JUPYTER_KERNEL#g" $JUPYTER_KERNEL_FOLDER/kernel.json
    sed -i -e "s#CUSTOM_SHIFTER_IMAGE#$IMAGE_NAME#g" $JUPYTER_KERNEL_FOLDER/kernel.json
    sed -i -e "s#CUSTOM_PYTHON_BIN#$CUSTOM_PYTHON_BIN#g" $JUPYTER_KERNEL_FOLDER/kernel.json
    sed -i -e "s#CUSTOM_PYTHONUSERBASE#$CUSTOM_PYTHONUSERBASE#g" $JUPYTER_KERNEL_FOLDER/kernel.json

    ## Install library
    mkdir -p $CUSTOM_PYTHONUSERBASE
    shifter --image=$IMAGE_NAME --env PYTHONUSERBASE=$CUSTOM_PYTHONUSERBASE \
            python3 -m pip install git+https://github.com/asnaylor/nersc_cluster_deploy.git --user
}

# setup_shifter_hvd_pytorch(){
#     IMAGE_NAME=$1
#     JUPYTER_KERNEL=$(echo $IMAGE_NAME | sed -r 's#[/:]+#_#g')
#     JUPYTER_KERNEL_FOLDER=$HOME/.local/share/jupyter/kernels/$JUPYTER_KERNEL/
#     CUSTOM_PYTHONUSERBASE=$HOME/.local/perlmutter/$JUPYTER_KERNEL

#     shifter --image=$IMAGE_NAME --module=gpu,nccl-2.15 \
#             --env PYTHONUSERBASE=$CUSTOM_PYTHONUSERBASE \
#             --env HOROVOD_NCCL_HOME=/opt/udiImage/modules/nccl-2.15 \
#             --env HOROVOD_GPU_OPERATIONS=NCCL \
#             --env HOROVOD_NCCL_LINK=SHARED \
#             --env HOROVOD_WITH_PYTORCH=1 \
#             python3 -m pip install horovod[pytorch]

# }

EX_NUM=$1

case $EX_NUM in

  1)
    echo "<> Setting up Ex1: Calculating Pi with Ray"
    setup_env pytorch/1.13.1
    ;;

  2)
    echo "<> Setting up Ex1: Tuning Hyperparameters of a Distributed PyTorch Model with PBT using Ray Train & Tune"
    setup_env pytorch/1.13.1
    ;;

  # 3) #current issue with hvd build `horovod.common.exceptions.HorovodInternalError: ncclAllReduce failed: unhandled cuda error`
  #   echo "<> Setting up Ex3: PyTorch MNIST Example: Ray + Horovod"
  #   setup_env pytorch/1.13.1
  #   setup_hvd_pytorch
  #   ;;

  *)
    echo "Not a valid exercise number..."
    echo $EX_NUM
    exit_abnormal
    ;;
esac

echo "<> Setup complete"
