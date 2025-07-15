#!/bin/bash

which pyenv >/dev/null
if ([ $? = 1 ]); then     
  echo Please install pyenv before installing this.
  exit 1
fi

pyenv update
pyenv install 3.12.9
pyenv global 3.12.9

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
cd ..

cp custom_nodes/ComfyUI-AI_Tools/extraStuff/run.* .
chmod 755 run.sh

uv pip install -r custom_nodes/ComfyUI-AI_Tools/requirements.txt
uv pip install -r requirements.txt

uv run playwright install
