#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pdf.py — 将 agent-learn 项目的 Markdown 章节合并并渲染成 PDF 书籍。

依赖：
    pip install markdown weasyprint pygments pyyaml

可选：
    npm install -g @mermaid-js/mermaid-cli    # 用于把 Mermaid 编译为 SVG

系统库（WeasyPrint 后端）：
    macOS:  brew install cairo pango gdk-pixbuf libffi
    Linux:  apt-get install libcairo2 libpango-1.0-0 libgdk-pixbuf2.0-0 libffi-dev

用法：
    python render_pdf.py
    python render_pdf.py --output mybook.pdf
    python render_pdf.py --render-mermaid        # 需已安装 mmdc
    python render_pdf.py --no-cover --no-toc
"""
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import markdown
import yaml
from markdown.extensions.toc import TocExtension
from weasyprint import HTML
from pygments.formatters.html import HtmlFormatter

# ---------------------------------------------------------------------------
# 常量 & 路径
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CHAPTERS_DIR = REPO_ROOT / "chapters"
DEFAULT_OUTPUT = REPO_ROOT / "agent-learn-book.pdf"
DEFAULT_META = REPO_ROOT / "book_meta.yaml"
CSS_PATH = REPO_ROOT / "book.css"

# 篇 → 章节范围（用于目录分组与运行时页眉）
PART_RANGES: list[tuple[str, range]] = [
    ("Part 1 · 基础篇",        range(1, 4)),     # Ch1-3
    ("Part 2 · 核心能力篇",    range(4, 8)),     # Ch4-7
    ("Part 3 · 框架原理篇",    range(8, 14)),    # Ch8-13
    ("Part 4 · 设计模式篇",    range(14, 19)),   # Ch14-18
    ("Part 5 · 工程架构篇",    range(19, 25)),   # Ch19-24
    ("Part 6 · 实战项目篇",    range(25, 29)),   # Ch25-28
    ("Part 7 · 前沿与展望",    range(29, 31)),   # Ch29-30
]

# 匹配 markdown 渲染后的 Mermaid 块
MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    re.DOTALL,
)
# 章节 H1 形如 "# Ch1｜标题" / "# Ch1 | 标题"
CHAPTER_H1_RE = re.compile(r"^#\s+Ch\d+\s*[｜|]\s*(.+?)\s*$", re.MULTILINE)


# ---------------------------------------------------------------------------
# 数据
# ---------------------------------------------------------------------------
@dataclass
class Chapter:
    number: int
    path: Path
    title: str               # 完整 H1，含 ChXX｜前缀
    clean_title: str         # 去掉前缀的标题
    body: str                # 原始 markdown
    part: str = ""           # 所属 Part

    @property
    def slug(self) -> str:
        return f"ch{self.number:02d}"


# ---------------------------------------------------------------------------
# 小工具
# ---------------------------------------------------------------------------
def log(msg: str) -> None:
    print(f"[render_pdf] {msg}", flush=True)


def part_of(n: int) -> str:
    for name, rng in PART_RANGES:
        if n in rng:
            return name
    return ""


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="将 agent-learn 项目的 Markdown 章节渲染为 PDF 书籍。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    p.add_argument("--chapters-dir", type=Path, default=DEFAULT_CHAPTERS_DIR,
                   help="章节目录（默认 chapters/）")
    p.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT,
                   help="输出 PDF 路径（默认 agent-learn-book.pdf）")
    p.add_argument("--meta", type=Path, default=DEFAULT_META,
                   help="书籍元数据 YAML 路径（不存在则使用默认）")
    p.add_argument("--render-mermaid", action="store_true",
                   help="若安装 mermaid-cli (mmdc)，把 Mermaid 编译为 SVG")
    p.add_argument("--mermaid-timeout", type=int, default=30,
                   help="mmdc 单次调用超时（秒）")
    p.add_argument("--no-toc", action="store_true", help="不生成目录页")
    p.add_argument("--no-cover", action="store_true", help="不生成封面")
    p.add_argument("--start", type=int, default=1, help="起始章节号（包含）")
    p.add_argument("--end", type=int, default=30, help="结束章节号（包含）")
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


# ---------------------------------------------------------------------------
# 章节收集
# ---------------------------------------------------------------------------
def collect_chapters(chapters_dir: Path,
                     start: int, end: int) -> list[Chapter]:
    if not chapters_dir.is_dir():
        raise SystemExit(f"章节目录不存在: {chapters_dir}")

    files = sorted(
        chapters_dir.glob("ch*.md"),
        key=lambda p: int(re.search(r"ch(\d+)", p.stem).group(1)),
    )
    chapters: list[Chapter] = []
    for path in files:
        n = int(re.search(r"ch(\d+)", path.stem).group(1))
        if n < start or n > end:
            continue
        text = path.read_text(encoding="utf-8")
        m = CHAPTER_H1_RE.search(text) or re.search(
            r"^#\s+(.+?)\s*$", text, re.MULTILINE
        )
        if m:
            if m.lastindex and m.lastindex >= 1 and m.group(1):
                clean = m.group(1).strip()
            else:
                clean = m.group(0).lstrip("# ").strip()
            title = f"Ch{n}｜{clean}"
        else:
            clean = path.stem
            title = path.stem
        chapters.append(Chapter(
            number=n, path=path, title=title, clean_title=clean,
            body=text, part=part_of(n),
        ))

    if not chapters:
        raise SystemExit(
            f"未在 {chapters_dir} 找到 ch{start:02d}-ch{end:02d}.md 章节文件"
        )
    return chapters


# ---------------------------------------------------------------------------
# Markdown → HTML
# ---------------------------------------------------------------------------
def md_to_html(md_text: str) -> str:
    """Markdown → HTML。Pygments 高亮、TOC 锚点、表格、列表扩展全开。"""
    return markdown.markdown(
        md_text,
        extensions=[
            "fenced_code",
            "tables",
            "attr_list",
            "def_list",
            "footnotes",
            "sane_lists",
            "smarty",
            TocExtension(toc_depth="2-3", anchorlink=False),
        ],
        output_format="html5",
    )


# ---------------------------------------------------------------------------
# Mermaid 处理
# ---------------------------------------------------------------------------
def _unescape(s: str) -> str:
    return (s.replace("&lt;", "<").replace("&gt;", ">")
             .replace("&amp;", "&").replace("&quot;", "\"")
             .replace("&#39;", "'"))


def _escape(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;"))


def _mermaid_placeholder(source: str) -> str:
    safe = _escape(source)
    return (
        '<figure class="mermaid-placeholder">'
        '<div class="mermaid-header">'
        '<span class="mermaid-tag">MERMAID 流程图</span>'
        '<span class="mermaid-hint">（PDF 静态占位 · 浏览器中可渲染）</span>'
        '</div>'
        f'<pre class="mermaid-source"><code>{safe}</code></pre>'
        '</figure>'
    )


def _mermaid_via_mmdc(source: str, timeout: int) -> str:
    if not shutil.which("mmdc"):
        return _mermaid_placeholder(source)
    try:
        with tempfile.TemporaryDirectory() as td:
            src = Path(td) / "in.mmd"
            out = Path(td) / "out.svg"
            cfg = Path(td) / "puppeteer.json"
            src.write_text(source, encoding="utf-8")
            cfg.write_text("{}", encoding="utf-8")
            subprocess.run(
                ["mmdc", "-i", str(src), "-o", str(out),
                 "-p", str(cfg), "-q", "--backgroundColor", "transparent"],
                check=True, timeout=timeout,
                capture_output=True,
            )
            svg = out.read_text(encoding="utf-8")
            # 去掉 SVG 自带 xmlns 命名空间重复（内联时无害）
            return f'<figure class="mermaid-figure">{svg}</figure>'
    except (subprocess.TimeoutExpired, subprocess.CalledProcessError,
            FileNotFoundError) as e:
        log(f"  ! mmdc 调用失败，回退占位: {e!r}")
        return _mermaid_placeholder(source)


def replace_mermaid(html: str, render: bool, timeout: int) -> str:
    def _repl(m: re.Match) -> str:
        src = _unescape(m.group(1))
        if render:
            return _mermaid_via_mmdc(src, timeout)
        return _mermaid_placeholder(src)
    return MERMAID_RE.sub(_repl, html)


# ---------------------------------------------------------------------------
# 目录
# ---------------------------------------------------------------------------
def build_toc_html(chapters: list[Chapter],
                   rendered: list[tuple[Chapter, str]]) -> str:
    """根据 H1（章节）+ H2/H3 标题生成两级目录，按 Part 分组。"""
    h_re = re.compile(r'<h([23])\s+id="([^"]+)">(.+?)</h\1>')

    items: list[dict] = []
    for ch, html in rendered:
        items.append({
            "level": 1, "anchor": ch.slug, "text": ch.clean_title,
            "num": f"Ch{ch.number:02d}", "part": ch.part,
        })
        for m in h_re.finditer(html):
            level = int(m.group(1))
            anchor = m.group(2)
            text = re.sub(r"<[^>]+>", "", m.group(3)).strip()
            items.append({
                "level": level, "anchor": anchor, "text": text,
                "num": "", "part": ch.part,
            })

    # 按 Part 分块渲染
    by_part: dict[str, list[dict]] = {}
    for it in items:
        by_part.setdefault(it["part"] or "其他", []).append(it)

    blocks: list[str] = []
    for part_name, group in by_part.items():
        if part_name and part_name != "其他":
            blocks.append(f'<li class="toc-part">{part_name}</li>')
        for it in group:
            if it["level"] == 1:
                blocks.append(
                    f'<li class="toc-l1"><a href="#{it["anchor"]}">'
                    f'<span class="toc-num">{it["num"]}</span>'
                    f'<span class="toc-text">{_escape(it["text"])}</span>'
                    f'</a></li>'
                )
            else:
                indent = "　" * (it["level"] - 2)
                blocks.append(
                    f'<li class="toc-l{it["level"]}"><a href="#{it["anchor"]}">'
                    f'{indent}{_escape(it["text"])}</a></li>'
                )
    return (
        '<section class="toc" id="toc">'
        '<h1>目  录</h1>'
        '<ul class="toc-list">' + "\n".join(blocks) + '</ul>'
        '</section>'
    )


# ---------------------------------------------------------------------------
# 封面
# ---------------------------------------------------------------------------
def render_cover(meta: dict) -> str:
    title = meta.get("title", "大模型 Agent 系统开发")
    subtitle = meta.get("subtitle", "从原理到架构")
    author = meta.get("author", "agent-learn 项目组")
    edition = meta.get("edition", "v1.0 · 2026")
    blurb = meta.get("blurb",
        "30 章 · 7 大篇章 · 系统讲透 LLM Agent 的设计原理、框架内核与工程架构。")
    pill = meta.get("pill", "LLM AGENT · 系统开发实战")
    return f"""
<section class="cover">
  <div class="cover-bg"></div>
  <div class="cover-content">
    <div class="cover-pill">{_escape(pill)}</div>
    <h1 class="cover-title">{_escape(title)}</h1>
    <div class="cover-subtitle">{_escape(subtitle)}</div>
    <div class="cover-divider"></div>
    <p class="cover-blurb">{_escape(blurb)}</p>
    <div class="cover-footer">
      <div class="cover-author">{_escape(author)}</div>
      <div class="cover-edition">{_escape(edition)}</div>
    </div>
  </div>
</section>
"""


# ---------------------------------------------------------------------------
# HTML 装配
# ---------------------------------------------------------------------------
def build_html(chapters: list[Chapter],
               rendered: list[tuple[Chapter, str]],
               meta: dict,
               include_toc: bool,
               include_cover: bool) -> str:
    if CSS_PATH.exists():
        css = CSS_PATH.read_text(encoding="utf-8")
    else:
        log("!! book.css 不存在，使用内联最简样式")
        css = _MINIMAL_CSS

    pygments_css = HtmlFormatter(style="monokai").get_style_defs(".codehilite")

    toc_html = build_toc_html(chapters, rendered) if include_toc else ""
    cover_html = render_cover(meta) if include_cover else ""

    body_sections = "\n".join(
        f'<section class="chapter" id="{ch.slug}">\n{html}\n</section>'
        for ch, html in rendered
    )

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{_escape(meta.get('title', 'Agent 系统开发'))}</title>
<style>
{css}
{pygments_css}
</style>
</head>
<body>
{cover_html}
{toc_html}
<main class="book-body">
{body_sections}
</main>
</body>
</html>"""


# 兜底 CSS（book.css 丢失时用）
_MINIMAL_CSS = """
@page { size: A4; margin: 2.4cm 2cm; }
body { font-family: "PingFang SC","Noto Sans CJK SC",sans-serif; line-height: 1.7; color:#222; }
h1 { color:#2c5282; border-bottom:3px solid #4a6fa5; padding-bottom:0.3em; page-break-before: always; }
h2 { color:#2c5282; border-left:5px solid #4a6fa5; padding-left:0.5em; }
pre,code { font-family:"JetBrains Mono",monospace; }
pre { background:#1e1e2e; color:#cdd6f4; padding:14px; border-radius:6px; }
code { background:#eef2f7; padding:1px 5px; border-radius:3px; }
table { border-collapse:collapse; width:100%; }
th,td { border:1px solid #cbd5e0; padding:8px 12px; }
th { background:#edf2f7; }
blockquote { border-left:5px solid #4a6fa5; background:#edf2f7; padding:0.6em 1em; }
.cover { page-break-after: always; }
.toc { page-break-after: always; }
.chapter { page-break-before: always; }
.mermaid-placeholder { border:2px dashed #94a3b8; padding:12px; background:#f8fafc; }
"""


# ---------------------------------------------------------------------------
# 入口
# ---------------------------------------------------------------------------
def main() -> int:
    args = parse_args()
    if args.verbose:
        log(f"参数: {args}")

    # 1. 元数据
    meta: dict = {}
    if args.meta.exists():
        try:
            meta = yaml.safe_load(args.meta.read_text(encoding="utf-8")) or {}
            log(f"已加载元数据: {args.meta}")
        except Exception as e:
            log(f"!! 读取 {args.meta} 失败: {e!r}，使用默认值")
    else:
        log("未找到 book_meta.yaml，使用默认元数据")

    # 2. 收集章节
    log(f"扫描章节: {args.chapters_dir}  (ch{args.start:02d}-ch{args.end:02d})")
    chapters = collect_chapters(args.chapters_dir, args.start, args.end)
    log(f"共 {len(chapters)} 章")

    # 3. Mermaid
    if args.render_mermaid:
        if shutil.which("mmdc"):
            log("mermaid-cli (mmdc) 可用，将尝试把图表编译为 SVG")
        else:
            log("!! --render-mermaid 已请求但未检测到 mmdc，将回退到占位卡片")
    else:
        log("Mermaid 占位模式（默认）。启用 --render-mermaid 可生成 SVG。")

    # 4. 渲染 Markdown
    rendered: list[tuple[Chapter, str]] = []
    for ch in chapters:
        log(f"  · {ch.slug}  {ch.title}")
        html = md_to_html(ch.body)
        html = replace_mermaid(html, args.render_mermaid, args.mermaid_timeout)
        rendered.append((ch, html))

    # 5. 拼装 HTML
    log("拼装 HTML 文档（封面 + 目录 + 30 章正文）")
    html_doc = build_html(
        chapters, rendered, meta,
        include_toc=not args.no_toc,
        include_cover=not args.no_cover,
    )

    # 6. WeasyPrint 渲染
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log(f"开始渲染 PDF → {args.output}")
    HTML(string=html_doc, base_url=str(REPO_ROOT)).write_pdf(target=args.output)

    # 7. 报告
    if args.output.exists():
        size_mb = args.output.stat().st_size / 1024 / 1024
        log(f"✅ 完成：{args.output}  ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
