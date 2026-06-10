# turtle 绘图

`turtle` 是 Python 内置的简易绘图模块，通过控制"海龟"在屏幕上移动来画图，适合编程入门和几何演示。

## 常用方法

| 方法 | 说明 |
|------|------|
| `forward(distance)` | 向前移动 |
| `backward(distance)` | 向后移动 |
| `left(angle)` / `right(angle)` | 左转 / 右转（角度） |
| `penup()` / `pendown()` | 抬笔 / 落笔 |
| `color(color)` | 设置画笔颜色 |
| `home()` | 回到原点 |
| `pos()` | 当前坐标 |
| `clearscreen()` | 清空画布 |

```python
import turtle

t = turtle.Turtle()
t.forward(100)
t.left(90)
t.forward(100)
t.color("red")
t.circle(50)
turtle.done()
```

## 最佳实践

1. 脚本末尾调用 `turtle.done()` 保持窗口不关闭。
2. 复杂图形可封装为函数，用循环减少重复代码。
3. 教学演示足够；正式可视化推荐 `matplotlib` 等库。
