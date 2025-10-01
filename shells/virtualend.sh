#!/bin/bash

# 加载 conda 环境
source /opt/conda/etc/profile.d/conda.sh
conda activate llmos

# 切换到项目目录
cd /root/PycharmProjects/LLMOS

# 启动 uvicorn
uvicorn VirtualEnd:app --reload --host 0.0.0.0 --port 3001
