# Jupyter Notebook 安装与使用总结

Jupyter Notebook 是一个基于浏览器的交互式开发环境，适合数据分析、教学演示、实验记录与 Python 学习。

## 1. 安装方式

## 1.1 推荐：使用虚拟环境安装

```bash
cd /Users/dreamerking/python
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
pip install notebook ipykernel
```

说明：
- `notebook`：经典 Jupyter Notebook 界面。
- `ipykernel`：Python 内核支持（让当前环境可被 Jupyter 使用）。

## 1.2 可选：安装 JupyterLab

```bash
pip install jupyterlab
```

`JupyterLab` 是更现代的界面，功能更完整；`Notebook` 更简洁。

## 2. 启动与关闭

### 2.1 启动 Notebook

```bash
jupyter notebook
```

启动后会自动打开浏览器（通常是 `http://localhost:8888`）。

### 2.2 指定端口并禁止自动打开浏览器

```bash
jupyter notebook --port=8890 --no-browser
```

### 2.3 停止服务

- 在终端按 `Ctrl + C`，然后输入 `y` 确认。

## 3. 创建与运行 Notebook

1. 打开页面后，点击 `New -> Python 3 (ipykernel)`。  
2. 在单元格输入代码。  
3. 按 `Shift + Enter` 执行并跳到下一格。  
4. 使用 `File -> Save and Checkpoint` 保存。  

## 4. 单元格类型

- `Code`：运行 Python 代码。
- `Markdown`：写笔记、标题、公式、说明。
- `Raw`：原始文本（较少用）。

Markdown 常见语法：
- 标题：`# 标题`
- 粗体：`**文字**`
- 代码块：```python ... ```

## 5. 常用快捷键（经典 Notebook）

### 5.1 模式说明
- 命令模式（蓝框）：用于管理单元格。
- 编辑模式（绿框）：用于编辑当前单元格内容。

### 5.2 高频快捷键
- `Enter`：进入编辑模式
- `Esc`：回到命令模式
- `Shift + Enter`：执行单元格并跳到下一格
- `Ctrl + Enter`：执行单元格并留在当前格
- `Alt + Enter`：执行并在下方插入新单元格
- `A`：在上方插入单元格（命令模式）
- `B`：在下方插入单元格（命令模式）
- `D D`：删除当前单元格（命令模式）
- `M`：切换为 Markdown
- `Y`：切换为 Code

## 6. 内核（Kernel）与环境管理

## 6.1 注册当前虚拟环境为内核

```bash
python -m ipykernel install --user --name py-learning --display-name "Python (py-learning)"
```

这样在 Notebook 页面可以选择你自己的内核，避免包版本混乱。

## 6.2 查看已安装内核

```bash
jupyter kernelspec list
```

## 6.3 删除内核

```bash
jupyter kernelspec uninstall py-learning
```

## 7. 常见工作流

1. 新建虚拟环境并安装依赖。  
2. 注册内核。  
3. 启动 Notebook。  
4. 使用 Markdown 记录思路，Code 单元做实验。  
5. 实验稳定后，把关键代码整理到 `.py` 模块中复用。  

## 8. 导出与分享

- 页面菜单：`File -> Download as` 导出为 `HTML`、`Markdown`、`Python` 等。
- 命令行导出：

```bash
jupyter nbconvert --to html demo.ipynb
jupyter nbconvert --to markdown demo.ipynb
jupyter nbconvert --to script demo.ipynb
```

## 9. 常见问题排查

- 端口占用：
  - 换端口：`--port=8890`
- 启动后打不开页面：
  - 复制终端输出中的完整链接（含 token）到浏览器。
- `ModuleNotFoundError`：
  - 通常是内核和安装包不在同一个 Python 环境，检查并切换正确内核。
- 单元格一直 `[*]`：
  - 可能死循环或阻塞，`Kernel -> Interrupt` 中断执行。
- 输出过多导致卡顿：
  - 清空输出：`Cell -> All Output -> Clear`。

## 10. 最小可执行流程（复制即用）

```bash
cd /Users/dreamerking/python
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip notebook ipykernel
python -m ipykernel install --user --name py-learning --display-name "Python (py-learning)"
jupyter notebook
```
