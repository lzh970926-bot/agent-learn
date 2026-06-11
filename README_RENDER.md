# PDF 渲染工具

`render_pdf.py` 把 `chapters/` 下 30 个章节的 Markdown 文件合并、排版后输出
**A4 中文 PDF 书籍**。样式在 `book.css` 中定义，封面文案在 `book_meta.yaml` 中配置。

---

## 1. 一句话用法

```bash
# 安装依赖（首次）
uv pip install -r requirements.txt          # 或 pip install -r requirements.txt

# 渲染
python render_pdf.py                        # 输出 agent-learn-book.pdf
```

## 2. 系统依赖

`weasyprint` 依赖 Cairo / Pango 等原生库，需要先安装：

| 系统    | 命令                                                                 |
|---------|----------------------------------------------------------------------|
| macOS   | `brew install cairo pango gdk-pixbuf libffi`                         |
| Ubuntu  | `sudo apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev` |
| Windows | 推荐使用 WSL，或在 [guruinstall](https://github.com/Kozea/WeasyPrint-docs) 找 wheel |

中文渲染需保证系统至少含一个中文字体（macOS 自带 PingFang SC，Linux 可装
`fonts-noto-cjk`）。

## 3. CLI 选项

```
python render_pdf.py [选项]

  --chapters-dir PATH   章节目录（默认 chapters/）
  --output, -o PATH     输出 PDF 路径（默认 agent-learn-book.pdf）
  --meta PATH           书籍元数据 YAML（默认 book_meta.yaml）
  --render-mermaid      启用 mermaid-cli 编译 Mermaid 为 SVG
  --mermaid-timeout N   mmdc 超时秒数（默认 30）
  --no-toc              关闭目录页
  --no-cover            关闭封面
  --start N             起始章节号（默认 1）
  --end N               结束章节号（默认 30）
  --verbose, -v         详细日志
```

### 部分使用场景

```bash
# 只渲染前 3 章做小样
python render_pdf.py --start 1 --end 3 --output ch01-03.pdf

# 关闭封面 + 目录，只出正文
python render_pdf.py --no-cover --no-toc

# 启用 Mermaid 图表（需先 npm i -g @mermaid-js/mermaid-cli）
python render_pdf.py --render-mermaid
```

## 4. 文件结构

```
agent-learn/
├── render_pdf.py        # 主脚本
├── book.css             # 排版样式（可直接编辑）
├── book_meta.yaml       # 封面文案
├── requirements.txt     # Python 依赖
├── README_RENDER.md     # 本文件
└── chapters/
    ├── ch01.md          # 输入
    ├── ch02.md
    └── ...
```

## 5. Mermaid 处理策略

| 模式              | 行为                                                         |
|-------------------|--------------------------------------------------------------|
| 默认（无 flag）   | 把每个 `mermaid` 代码块替换成带"MERMAID 流程图"标签的占位卡，源文件作为代码高亮展示在卡片中 |
| `--render-mermaid`| 调用 `mmdc`（mermaid-cli）把图表编译为 SVG 嵌入 PDF          |
| `mmdc` 未安装     | 自动回退到占位卡模式，并在终端提示                           |

> **为什么默认用占位卡？**  浏览器/HTML 里的 Mermaid 是 JS 在客户端渲染的，
> 静态 PDF 渲染器（WeasyPrint、Chromium headless、Pandoc）都不会跑 JS。
> 想要矢量 SVG 必须先编译，占位卡可以让 PDF 即开即用、信息不丢失。

## 6. 排版约定一览

| 元素       | 样式说明                                                       |
|------------|----------------------------------------------------------------|
| 字体       | 中文 `PingFang SC` / `Noto Sans CJK SC` 优先；等宽 `JetBrains Mono` |
| 页面       | A4；上 2.6cm / 下 2.8cm / 左右 2.2cm                           |
| 页眉       | 左：当前章标题（自动）· 右：书名                                |
| 页脚       | 居中：`当前页 / 总页数`                                        |
| 封面       | 紫蓝渐变背景，渐变光斑，`#book_meta.yaml` 控制文案              |
| 目录       | 罗马数字页码；按 Part 分组的二级目录（H1+H2+H3）                 |
| 章节首     | `h1` 自动跨页（`page-break-before: always`）                   |
| 代码块     | Catppuccin / Monokai 暗色主题；圆角阴影；尽量不分页              |
| 表格       | 表头渐变 + 隔行斑马纹；表头跨页重复                             |
| 引用       | 左侧色条 + 浅灰底；首条引用作为"本章目标"以金黄底色突出         |

修改 `book.css` 即可重新调整风格，重跑脚本即时生效。

## 7. 常见问题

**Q：生成的 PDF 没有中文？**  
A：系统未安装中文字体。Linux 装 `fonts-noto-cjk`；macOS 自带 PingFang SC。

**Q：WeasyPrint 启动报 "no library called cairo"？**  
A：系统库未装，按 §2 安装。

**Q：Mermaid 图表在 PDF 里是空的？**  
A：用 `--render-mermaid` 编译为 SVG；或者保留占位卡，源在浏览器/GitHub 同样可读。

**Q：页眉跑到了封面/目录上？**  
A：检查 `book.css` 里 `@page cover` 与 `@page toc` 的 `content: ""` 规则。
   也可用 `--no-cover --no-toc` 验证是否脚本问题。
