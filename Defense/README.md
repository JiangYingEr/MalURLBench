# URLGuard



URLGuard is an external module for filtering malicious URLs built with QLoRA-finetuned LoRA adapter. This repository contains code and environment snapshots for the URLGuard. The LoRA adapter weights are hosted on Hugging Face. 

**Note:** Training outputs an adapter (LoRA weights + config), NOT a standalone full model checkpoint. Therefore you must load the **base model** first, then attach the adapter.



## Adapter Weights
Download the LoRA adapter from Hugging Face: https://huggingface.co/nonamehhh/URLGuard
- Adapter repo: `nonamehhh/URLGuard`

It includes:

- `adapter_config.json`

- `adapter_model.safetensors`

- tokenizer + chat template files

You can load it directly from Hugging Face, or download it first.



## Quick Start



### File Overview



- `train_qlora_new.py`  

&nbsp; QLoRA training script (saves **adapter-only** checkpoints to `--out_dir`).



- `requirements.txt`  

&nbsp; Pip dependencies snapshot.



- `condaenv.yml`  

&nbsp; Conda environment snapshot used during training.



- `torch_env.txt`, `nvidia-smi.txt`  

&nbsp; Hardware / CUDA / PyTorch snapshot for reproducibility.



## Environment Setup



```bash

conda env create -f condaenv.yml

conda activate metagpt311

python -m pip install -r requirements.txt
