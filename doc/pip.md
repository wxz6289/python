# pip 常见用法总结

## 什么是 pip？

pip 是 Python 的包管理工具，用于安装、升级、卸载和管理 Python 包（库）。

---

## 1. 安装包

### 安装最新版本的包
```bash
pip install package_name
```

### 安装指定版本
```bash
pip install package_name==2.0.0
```

### 安装版本范围
```bash
pip install "package_name>=1.0,<2.0"
```

### 升级包
```bash
pip install --upgrade package_name
```

### 升级 pip 自身
```bash
pip install --upgrade pip
```

---

## 2. 卸载包

```bash
pip uninstall package_name
```

批量卸载（从文件）：
```bash
pip uninstall -r requirements.txt -y
```

---

## 3. 查看已安装的包

### 列出所有已安装的包
```bash
pip list
```

### 以requirements格式输出
```bash
pip freeze
```

### 查看过期包（可更新的包）
```bash
pip list --outdated
```

### 查看某个包的详细信息
```bash
pip show package_name
```

---

## 4. requirements.txt 文件

### 生成 requirements.txt
```bash
pip freeze > requirements.txt
```

### 从 requirements.txt 安装所有依赖
```bash
pip install -r requirements.txt
```

### requirements.txt 格式示例
```
requests==2.28.1
numpy>=1.21.0
pandas
flask>=2.0,<3.0
```

---

## 5. 搜索包

```bash
pip search package_name
```

> ⚠️ 注意：PyPI 已禁用 `pip search` 功能，建议使用 https://pypi.org 网站搜索包。

---

## 6. 源管理（镜像源）

### 临时使用镜像源安装包
```bash
pip install package_name -i https://pypi.tuna.tsinghua.edu.cn/simple
```

### 永久配置镜像源

创建或编辑配置文件：

**macOS/Linux:**
```bash
~/.pip/pip.conf
```

**Windows:**
```
%APPDATA%\pip\pip.ini
```

配置内容：
```ini
[global]
index-url = https://pypi.tuna.tsinghua.edu.cn/simple
trusted-host = pypi.tuna.tsinghua.edu.cn
```

### 常用国内镜像源
- 清华大学：`https://pypi.tuna.tsinghua.edu.cn/simple`
- 阿里云：`https://mirrors.aliyun.com/pypi/simple/`
- 豆瓣：`https://pypi.douban.com/simple/`
- 中科大：`https://pypi.mirrors.ustc.edu.cn/simple/`

---

## 7. 虚拟环境

### 创建虚拟环境
```bash
python -m venv myenv
```

### 激活虚拟环境

**macOS/Linux:**
```bash
source myenv/bin/activate
```

**Windows:**
```
myenv\Scripts\activate
```

### 退出虚拟环境
```bash
deactivate
```

### 在虚拟环境中安装包
激活虚拟环境后，所有 `pip` 命令都只影响当前虚拟环境。

---

## 8. 其他常用命令

### 查看已安装的包文件位置
```bash
pip show package_name
# 查看 Location 字段
```

### 检查环境中的包兼容性
```bash
pip check
```

### 缓存管理

查看缓存目录：
```bash
pip cache dir
```

清除缓存：
```bash
pip cache purge
```

列出缓存文件：
```bash
pip cache list
```

### 安装包但不安装依赖
```bash
pip install --no-deps package_name
```

### 仅下载包（不安装）
```bash
pip download package_name -d ./packages
```

### 从本地目录安装
```bash
pip install ./path/to/package.whl
pip install ./path/to/package.tar.gz
```

### 安装开发模式（可编辑模式）
```bash
pip install -e .
```

---

## 9. 常见问题排查

### 安装超时
```bash
pip install --timeout 100 package_name
```

### 强制重新安装
```bash
pip install --force-reinstall package_name
```

### 忽略已安装的包（不检查依赖）
```bash
pip install --no-dependencies package_name
```

### 显示详细安装信息（调试用）
```bash
pip install -v package_name
```

---

## 10. pip 命令速查表

| 命令                              | 说明                   |
|-----------------------------------|------------------------|
| `pip install <package>`           | 安装包                 |
| `pip install -r requirements.txt` | 从文件安装             |
| `pip uninstall <package>`         | 卸载包                 |
| `pip list`                        | 列出所有已安装的包     |
| `pip freeze`                      | 以requirements格式输出 |
| `pip show <package>`              | 显示包详细信息         |
| `pip search <package>`            | 搜索包（已禁用）         |
| `pip install --upgrade <package>` | 升级包                 |
| `pip cache list`                  | 查看缓存               |
| `pip cache purge`                 | 清除缓存               |
| `pip check`                       | 检查依赖兼容性         |
| `pip download`                    | 仅下载不安装           |
| `pip install -e .`                | 开发模式安装           |

---

## 11. pip3 常见用法

### 什么是 pip3？

`pip3` 是 pip 的 Python 3 版本。在同时安装 Python 2 和 Python 3 的系统上，`pip` 可能指向 Python 2 的包管理器，而 `pip3` 明确指向 Python 3。

### pip 与 pip3 的关系

- 在只安装了 Python 3 的系统上，`pip` 和 `pip3` 通常是**同一个命令**
- 可以使用 `pip --version` 查看关联的 Python 版本

```bash
pip --version   # 查看关联的Python版本
pip3 --version  # 查看关联的Python版本
```

### pip3 常用命令

pip3 的命令与 pip **完全相同**，只是明确指定使用 Python 3 环境：

```bash
pip3 install package_name
pip3 install -r requirements.txt
pip3 list
pip3 uninstall package_name
pip3 freeze > requirements.txt
```

### 何时使用 pip3？

- 系统同时安装 Python 2 和 Python 3
- 需要确保包安装到 Python 3 环境
- 脚本中明确指定 Python 3 依赖

> 💡 **最佳实践**：推荐使用 `python3 -m pip install <package>` 替代 `pip3 install <package>`，这样可以确保包安装到正确的 Python 版本。

---

## 12. conda 常见用法

### 什么是 conda？

conda 是一个开源的包管理和环境管理系统，最初为 Python 设计，但现在支持**任何语言**的包。它是 Anaconda 和 Miniconda 发行版的核心工具。

### 环境管理

#### 创建环境
```bash
# 创建Python环境
conda create --name myenv python=3.9

# 创建环境并安装包
conda create --name myenv python=3.9 numpy pandas

# 指定Python版本范围
conda create --name myenv python>=3.8,<3.11
```

#### 环境操作
```bash
# 列出所有环境
conda env list
conda info --envs

# 激活环境
conda activate myenv

# 退出当前环境
conda deactivate

# 删除环境
conda env remove --name myenv

# 克隆环境
conda create --name newenv --name oldenv
```

### 包管理

#### 安装包
```bash
# 安装包
conda install package_name

# 安装指定版本
conda install package_name=2.0.0

# 从指定channel安装
conda install -c conda-forge package_name

# 更新包
conda update package_name

# 更新所有包
conda update --all
```

#### 查看和管理已安装的包
```bash
# 列出已安装的包
conda list

# 搜索可用的包
conda search package_name

# 卸载包
conda remove package_name

# 清理无用包和缓存
conda clean --all
```

### 环境导出与导入

#### 导出环境配置
```bash
# 导出完整配置（包含conda和pip包）
conda env export > environment.yml

# 仅导出用户安装的包
conda env export --no-builds > environment.yml

# 导出pip包到requirements.txt
pip freeze > requirements.txt
```

#### 从文件创建环境
```bash
# 从yml文件创建
conda env create -f environment.yml

# 从requirements.txt创建（有限支持）
pip install -r requirements.txt
```

#### environment.yml 示例
```yaml
name: myenv
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.9
  - numpy>=1.21
  - pandas
  - pip
  - pip:
    - requests==2.28.1
    - flask>=2.0
```

### Channel 管理

#### 查看当前channels
```bash
conda config --show channels
```

#### 添加channel
```bash
conda config --add channels conda-forge
conda config --add channels defaults
```

#### 设置channel优先级
```bash
conda config --set channel_priority strict
```

#### 常用channels
- `defaults`: conda默认的软件源
- `conda-forge`: 社区维护的大型软件源（推荐）
- `bioconda`: 生物信息学软件源
- `pytorch`: PyTorch官方源

### conda 配置

```bash
# 显示当前配置
conda config --show

# 添加镜像源（以清华源为例）
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/cloud/conda-forge/
conda config --set show_channel_urls yes

# 查看配置文件
conda config --show-sources
```

---

## 13. pip、pip3 与 conda 对比

### 核心对比表

| 特性         | pip            | pip3           | conda                            |
|--------------|----------------|----------------|----------------------------------|
| **包来源**   | PyPI           | PyPI           | conda channels                   |
| **包格式**   | wheel, sdist   | wheel, sdist   | conda package (.tar.bz2, .conda) |
| **语言支持** | 仅Python       | 仅Python       | 任意语言                         |
| **环境管理** | ❌ (需配合venv) | ❌ (需配合venv) | ✅ 内置                           |
| **二进制包** | 部分支持       | 部分支持       | ✅ 完整支持                       |
| **依赖解析** | 基础           | 基础           | 高级（SAT求解器）                  |
| **系统依赖** | 不管理         | 不管理         | ✅ 可管理                         |
| **跨平台**   | ✅              | ✅              | ✅                                |
| **安装速度** | 较快           | 较快           | 较慢（但mamba可加速）              |

### 详细对比

#### 1. 包管理能力

| 维度     | pip/pip3               | conda             |
|----------|------------------------|-------------------|
| 包数量   | 30万+（PyPI）            | 2万+（conda-forge） |
| 更新频率 | 非常快（开发者直接上传） | 较慢（需要打包）    |
| 包质量   | 参差不齐               | 较高（经过审核）    |
| 依赖解析 | 简单（可能冲突）         | 严格（避免冲突）    |

#### 2. 环境管理

| 维度       | pip + venv           | conda          |
|------------|----------------------|----------------|
| 创建速度   | 快（复制Python标准库） | 慢（下载所有包） |
| 磁盘占用   | 较小                 | 较大           |
| Python版本 | 系统已安装的版本     | 可安装任意版本 |
| 非Python包 | ❌                    | ✅（如R、C库）     |
| 隔离性     | 仅Python包           | 完整环境隔离   |

#### 3. 适用场景

| 场景                    | 推荐工具 |
|-------------------------|----------|
| 纯Python项目            | pip/pip3 |
| 数据科学/机器学习       | conda    |
| 需要特定Python版本      | conda    |
| 需要非Python依赖（如C库） | conda    |
| 简单脚本/小项目         | pip/pip3 |
| 大型团队项目            | conda    |
| Web开发                 | pip/pip3 |
| 科学研究                | conda    |

### 混合使用

pip 和 conda **可以一起使用**，但需注意：

```yaml
# environment.yml
name: myenv
dependencies:
  - python=3.9
  - numpy
  - pip
  - pip:
    - some-pip-only-package
```

**注意事项**：
1. 先用 conda 安装包，再用 pip 安装剩余包
2. 避免用 pip 覆盖 conda 安装的包
3. 在 conda 环境中运行 `pip install`，包会安装到当前环境
4. 使用 `conda list` 可查看 conda 和 pip 安装的包

### 选择建议

```
你的项目需要什么？
├── 仅Python包
│   ├── 简单项目 → pip/pip3 + venv
│   └── 复杂依赖 → pip/pip3 + virtualenv/pipenv
│
└── 需要非Python包或特定Python版本
    └── conda（或mamba加速）
```

### mamba：conda 的加速替代品

[mamba](https://github.com/mamba-org/mamba) 是 conda 的 C++ 重写版本， significantly faster：

```bash
# 安装mamba
conda install mamba -n base -c conda-forge

# 使用mamba（命令与conda完全相同）
mamba install numpy
mamba create --name myenv python=3.9
mamba env update -f environment.yml
```

---

## 提示

- 使用 `pip --version` 查看 pip 版本
- 使用 `pip --help` 查看所有可用命令
- 使用 `pip <command> --help` 查看具体命令的帮助
- 建议使用虚拟环境隔离项目依赖
- 定期运行 `pip list --outdated` 检查更新
- 使用 `python3 -m pip` 替代 `pip3` 确保版本正确
- 使用 `conda info` 查看 conda 环境信息
- 数据科学项目优先考虑 conda
