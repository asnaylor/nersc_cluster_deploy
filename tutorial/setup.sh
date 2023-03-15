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

setup_conda() {
    CONDA_RAY_ENV=nersc_cluster_deploy
    module load python
    #Create conda env
    conda create -n $CONDA_RAY_ENV ipykernel python=3.10 -y

    #Install library
    source activate $CONDA_RAY_ENV
    python3 -m pip install git+https://github.com/asnaylor/nersc_cluster_deploy.git
    python3 -m ipykernel install --user --name $CONDA_RAY_ENV --display-name $CONDA_RAY_ENV
    source deactivate
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

setup_shifter_hvd_pytorch(){
    IMAGE_NAME=$1
    JUPYTER_KERNEL=$(echo $IMAGE_NAME | sed -r 's#[/:]+#_#g')
    JUPYTER_KERNEL_FOLDER=$HOME/.local/share/jupyter/kernels/$JUPYTER_KERNEL/
    CUSTOM_PYTHONUSERBASE=$HOME/.local/perlmutter/$JUPYTER_KERNEL

    shifter --image=$IMAGE_NAME --module=gpu,nccl-2.15 \
            --env PYTHONUSERBASE=$CUSTOM_PYTHONUSERBASE \
            --env HOROVOD_NCCL_HOME=/opt/udiImage/modules/nccl-2.15 \
            --env HOROVOD_GPU_OPERATIONS=NCCL \
            --env HOROVOD_NCCL_LINK=SHARED \
            --env HOROVOD_WITH_PYTORCH=1 \
            python3 -m pip install horovod[pytorch]

}

EX_NUM=$1

case $EX_NUM in

  1)
    echo "<> Setting up Ex1: Calculating Pi with Ray"
    setup_conda
    ;;

  2)
    echo "<> Setting up Ex2: PyTorch MNIST Example: Ray + Horovod"
    setup_shifter_kernel nersc/pytorch:ngc-22.09-v0 /opt/conda/bin/python
    setup_shifter_hvd_pytorch nersc/pytorch:ngc-22.09-v0
    ;;

  *)
    echo "Not a valid exercise number..."
    echo $EX_NUM
    exit_abnormal
    ;;
esac

echo "<> Setup complete"
