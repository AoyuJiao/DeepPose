# DeepPose

DeepPose is a workflow for **protein–ligand binding pose prediction and scoring**.

It integrates two tools:

* **FABind** – predicts ligand binding poses
* **GNINA** – scores predicted binding poses

---

# Scoring Metrics

GNINA produces two metrics:

| Metric      | Description                            |
| ----------- | -------------------------------------- |
| CNNScore    | Confidence (0–1) of the predicted pose |
| CNNaffinity | Predicted binding affinity             |

Both metrics are **larger-is-better**.

Tests show **no significant correlation** between the two metrics (P-value ≫ 0.05).

To combine them, **TOPSIS** is recommended for multi-criteria evaluation.

---

# Large Files

Some large files are **not included in this repository**.

Download them from Baidu Netdisk:

https://pan.baidu.com/s/1PA05Xmiw93KudSruvXzf6Q?pwd=jcp8

Files included in the archive:

```
best_model.bin
pdbbind2020.tar
gnina1.3.2
```

After downloading, place them in the following locations:

```
DeepPose/
├── FABind/
│   ├── ckpt/
│   │   └── best_model.bin
│   └── pdbbind2020/
│
└── GNINA/
    └── gnina1.3.2
```

---

# Installation

DeepPose requires a **Linux environment**.

Recommended environment:

```
CUDA 11.3
PyTorch 1.12.0
RDKit 2021.03.4
```

WSL2 Ubuntu is also supported.

---

# 1 FABind Installation

## 1.1 Environment Setup

```
sudo apt-get install git-lfs
git lfs install

git clone https://github.com/AoyuJiao/DeepPose.git --recursive
cd DeepPose/FABind
```

Create conda environment:

```
conda create --name fabind python=3.8
conda activate fabind
```

Install PyTorch:

```
conda install pytorch==1.12.0 torchvision==0.13.0 torchaudio==0.12.0 cudatoolkit=11.3 -c pytorch
```

Install PyG dependencies:

```
pip install https://data.pyg.org/whl/torch-1.12.0%2Bcu113/torch_cluster-1.6.0%2Bpt112cu113-cp38-cp38-linux_x86_64.whl
pip install https://data.pyg.org/whl/torch-1.12.0%2Bcu113/torch_scatter-2.1.0%2Bpt112cu113-cp38-cp38-linux_x86_64.whl
pip install https://data.pyg.org/whl/torch-1.12.0%2Bcu113/torch_sparse-0.6.15%2Bpt112cu113-cp38-cp38-linux_x86_64.whl
pip install https://data.pyg.org/whl/torch-1.12.0%2Bcu113/torch_spline_conv-1.2.1%2Bpt112cu113-cp38-cp38-linux_x86_64.whl
pip install https://data.pyg.org/whl/torch-1.12.0%2Bcu113/pyg_lib-0.2.0%2Bpt112cu113-cp38-cp38-linux_x86_64.whl
```

Install additional packages:

```
pip install torch-geometric==2.4.0
pip install torchdrug==0.1.2 torchmetrics==0.10.2 tqdm mlcrate pyarrow accelerate Bio lmdb fair-esm tensorboard
pip install fair-esm
pip install rdkit-pypi==2021.03.4
```

Install OpenBabel:

```
conda install -c conda-forge openbabel
```

---

## 1.2 Add FABind Command

```
mkdir -p ~/bin
cp fabind-run ~/bin/fabind-run
chmod +x ~/bin/fabind-run
```

Edit `.bashrc`:

```
nano ~/.bashrc
```

Add:

```
export PATH="$HOME/bin:$PATH"
```

Apply changes:

```
source ~/.bashrc
```

---

## 1.3 Model and Dataset

Place the downloaded files:

```
FABind/
 ├── ckpt/
 │    └── best_model.bin
 └── pdbbind2020/
```

Extract dataset:

```
tar -xf pdbbind2020.tar
```

---

## 1.4 Generate ESM2 Features

```
data_path=pdbbind2020
python fabind/tools/generate_esm2_t33.py ${data_path}
```

⚠ This step is **time-consuming**.

---

## 1.5 Run FABind

```
fabind-run
```

---

# 2 GNINA Installation

## 2.1 Environment Setup

```
conda create -n gnina python=3.9 -y
conda activate gnina
conda install pandas -y
```

Verify installation:

```
python -c "import pandas; print(pandas.__version__)"
```

---

## 2.2 Install GNINA

Place the downloaded binary:

```
sudo cp gnina1.3.2 /usr/local/bin/gnina
sudo chmod 755 /usr/local/bin/gnina
```

Install helper script:

```
cp gnina-run /usr/local/bin/gnina-run
sudo chmod 755 /usr/local/bin/gnina-run
```

---

# Usage

## Predict Binding Poses

Prepare directory structure similar to:

```
FABind/inference
```

Example:

```
project/
 ├── pdb_files/
 │    └── receptor.pdb
 └── index.csv
```

Notes:

* Remove **water molecules and existing ligands**
* Recommended: **one protein per directory**

Run FABind:

```
fabind-run
```

FABind requires **GPU**.

Avoid running multiple GPU tasks simultaneously.

---

## Score Poses with GNINA

After FABind finishes:

```
gnina-run
```

Supported version:

```
gnina 1.3.2
```

---

# Results

## FABind Output

```
inference_output/
```

Contains:

* ligand coordinates
* bond connectivity

Visualization requires loading **receptor PDB together with ligand**.

---

## GNINA Output

```
gnina_scoring_summary.csv
```

Contains:

* CNNScore
* CNNaffinity
* scoring summary

---

# Citation

If you use this workflow, please cite the following works.

## FABind

```
@article{pei2023fabind,
  title={FABind: Fast and Accurate Protein-Ligand Binding},
  author={Pei, Qizhi and Gao, Kaiyuan and Wu, Lijun and Zhu, Jinhua and Xia, Yingce and Xie, Shufang and Qin, Tao and He, Kun and Liu, Tie-Yan and Yan, Rui},
  journal={arXiv preprint arXiv:2310.06763},
  year={2023}
}

@inproceedings{pei2023fabind,
  title={{FAB}ind: Fast and Accurate Protein-Ligand Binding},
  author={Qizhi Pei and Kaiyuan Gao and Lijun Wu and Jinhua Zhu and Yingce Xia and Shufang Xie and Tao Qin and Kun He and Tie-Yan Liu and Rui Yan},
  booktitle={Thirty-seventh Conference on Neural Information Processing Systems},
  year={2023},
  url={https://openreview.net/forum?id=PnWakgg1RL}
}
```

## GNINA

```
McNutt A, Li Y, Meli R, Aggarwal R, Koes DR.  
GNINA 1.3: the next increment in molecular docking with deep learning.  
Journal of Cheminformatics, 2025.

McNutt A, Francoeur P, Aggarwal R, Masuda T, Meli R, Ragoza M, Sunseri J, Koes DR.  
GNINA 1.0: Molecular docking with deep learning.  
Journal of Cheminformatics, 2021.

Ragoza M, Hochuli J, Idrobo E, Sunseri J, Koes DR.  
Protein–Ligand Scoring with Convolutional Neural Networks.  
Journal of Chemical Information and Modeling, 2017.
```

---

# License

Please follow the licenses of the original projects:

* FABind
* GNINA
