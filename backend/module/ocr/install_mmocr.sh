conda create --name openmmlab python=3.8 -y
conda activate openmmlab
conda install pytorch==1.10.1 torchvision==0.11.2 torchaudio==0.10.1 cudatoolkit=11.3 -c pytorch -c conda-forge
pip install -U openmim
mim install mmcv-full==1.5.0
pip install mmdet==2.21.0
pip install -r requirements.txt
pip install -v -e .