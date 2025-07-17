#!/bin/bash

which pyenv >/dev/null
if ([ $? = 1 ]); then     
  echo Please install pyenv before installing this.
  exit 1
fi

export PATH="`echo "$PATH" | awk -F ":" 'BEGIN {IGNORECASE=1;first=1} { print FN; for(i=1;i <= NF; i=i+1) { if(match($i,"python") == 0) {if(first!=1) printf(":"); printf("%s",$i); first=0} } }'`"
unexport PYTHONPATH
unexport PYTHON_PATH

pyenv update
pyenv install 3.12.9
pyenv global 3.12.9

pythonVersion=`python --version`

if ([ "$pythonVersion" != "Python 3.12.9" ]); then
  echo Python version error. Should be 3.12.9 but recieved $pythonVersion
  echo
  exit 1
fi

python -m pip install -U pip
pip install uv
cd ~
git clone https://github.com/comfyanonymous/ComfyUI ComfyUI
cd ~/ComfyUI

uv venv
uv pip install pip comfy-cli 
uv run comfy set-default .
uv run comfy install --restore

cd custom_nodes
git clone https://github.com/qlikpetersen/ComfyUI-AI_Tools
git clone https://github.com/lks-ai/anynode
cd ..

cp custom_nodes/ComfyUI-AI_Tools/extraStuff/run.* .
chmod 755 run.sh

uv pip install -r requirements.txt
uv pip install -r custom_nodes/anynode/requirements.txt
uv pip install -r custom_nodes/ComfyUI-AI_Tools/requirements.txt

uv run playwright install

echo
echo Execute run.bat or run.sh from `pwd` to start ComfyUI

echo Press Enter to continue.
read