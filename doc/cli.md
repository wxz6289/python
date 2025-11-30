# Python 命令行操作归类整理

## 1. 解释器与交互式环境

`解释器输入参数`: 解释器读取命令行参数，把脚本名与其他参数转化为字符串列表存到 sys 模块的 argv 变量里。执行 import sys，可以导入这个模块，并访问该列表。该列表最少有一个元素；未给定输入参数时，sys.argv[0] 是空字符串。给定脚本名是 '-' （标准输入）时，sys.argv[0] 是 '-'。使用 -c command 时，sys.argv[0] 是 '-c'。如果使用选项 -m module，sys.argv[0] 就是包含目录的模块全名。解释器不处理 -c command 或 -m module 之后的选项，而是直接留在 sys.argv 中由命令或模块来处理。

```bash
python hello.py

// #!/usr/bin/env python3
chmod +x hello.py
./hello.py
```

```bash
# 查看 Python 版本
python --version
# 执行一段命令
python -c 'print("Hello")'
# 以模块方式运行
python -m module [args]
python -m http.server 8080
# 进入交互式模式
python -i
# 从源码安装包
python setup.py install
# 使用 IPython 交互式解释器
ipython
# 启动 Jupyter Notebook
jupyter notebook
# 查看函数签名（IPython/Jupyter）
function?
# 查看上一次结果（IPython/Jupyter）
_
# 查看帮助信息
help([object])
```

编码声明

```py
#!/usr/bin/env python
# -*- encoding name -*-
# name => utf-8(默认) latin-1
```

## 2. 包管理工具

```bash
# 查看 Python 路径
which python
# 查看 pip 路径
which pip
# 列出已安装包
pip list
# 安装常用科学计算包
pip install ipython scipy numpy pandas matplotlib jupyter

# 安装指定版本包
pip install package==1.2.3

# 升级包
pip install --upgrade package
pip install -U package
# 卸载包
pip uninstall package
# 查看包详细信息
pip show package
# 升级 pip
python -m pip install --upgrade pip
# 检查 pip 版本
python -m pip --version

```

---

## 3. 虚拟环境管理

```bash

# 使用 venv 创建虚拟环境
python3 -m venv myenv

# 或使用 virtualenv 创建虚拟环境
# 进入指定目录
cd $ML_PATH
# 安装 virtualenv
python -m pip install --user -U virtualenv
# 创建环境
python3 -m virtualenv ml-action
# 激活环境（示例）
source ml-action/bin/activate
# 退出虚拟环境
deactivate

virtualenv ml-action
source ml-action/bin/activate
conda deactivate
```

## 4. Anaconda/Miniconda 环境管理
conda 管理和部署应用、环境和包的工具

```bash
# 下载 Miniconda
curl https://repo.anaconda.com/miniconda/Miniconda3-latest-MacOSX-arm64.sh -o ~/miniconda3/miniconda.sh
# 安装 Miniconda
bash ~/miniconda3/miniconda.sh -b -u -p ~/miniconda3
rm -rf ~/miniconda3/miniconda.sh
# 初始化 shell
~/miniconda3/bin/conda init bash
~/miniconda3/bin/conda init zsh
# 查看 conda 路径
which conda
# 激活环境
conda activate
# 关闭环境
conda deactivate
# 列出所有环境
conda env list
# 删除环境
conda remove -n myenv --all
# 导出环境
conda env export > environment.yml
# 导入环境
conda env create -f environment.yml

# 查看已安装包
conda list
# 查看环境信息
conda info --envs
# 激活环境
conda activate clawer
# 退出环境
conda deactivate
```

## 清屏

```py
import os
os.system('clear') // mac and linux
os.system('cls') // windos
os.system('reset') // linux
os.system("printf'\033c'") // linux
```

- [virtualenv](https://virtualenv.pypa.io/en/latest/)
- [venv](https://docs.python.org/zh-cn/3/library/venv.html)
- [Anaconda](https://www.anaconda.com/download)
- [Miniconda](https://docs.anaconda.com/free/miniconda/index.html)

