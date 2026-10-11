Install a virtual environment for CircleCircle2

Use Conda (Anaconda Prompt):

1. Create a new env: "conda create -n circlecircle2 python=3.10 -y"

2. get local CUDA version: "nvidia-smi"

3. install PyTorch GPU Version: conda install pytorch torchvision torchaudio pytorch-cuda=13.2 -c pytorch -c nvidia -y
!!!!  you need to replace 13.2 to your true local CUDA version.
