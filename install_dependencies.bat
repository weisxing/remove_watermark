@echo off
chcp 65001
echo 正在创建并激活conda环境...
conda env create -n imgToolEnv -f environment.yml
conda activate imgToolEnv
echo 依赖安装完成！ 