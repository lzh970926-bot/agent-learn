#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
render_pdf_playwright.py — 使用 Playwright (Chromium) 将 Markdown 章节渲染为 PDF。

依赖：markdown pygments pyyaml playwright
用法：python3 render_pdf_playwright.py
"""
from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path

import markdown
import yaml
from markdown.extensions.toc import TocExtension
from playwright.sync_api import sync_playwright
from pygments.formatters.html import HtmlFormatter

# ---------------------------------------------------------------------------
# 常量 & 路径
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parent
DEFAULT_CHAPTERS_DIR = REPO_ROOT / "chapters"
DEFAULT_OUTPUT = REPO_ROOT / "agent-learn-book.pdf"
DEFAULT_META = REPO_ROOT / "book_meta.yaml"
CSS_PATH = REPO_ROOT / "book.css"

PART_RANGES: list[tuple[str, range]] = [
    ("Part 1 · 基础篇",        range(1, 4)),
    ("Part 2 · 核心能力篇",    range(4, 8)),
    ("Part 3 · 框架原理篇",    range(8, 14)),
    ("Part 4 · 设计模式篇",    range(14, 19)),
    ("Part 5 · 工程架构篇",    range(19, 25)),
    ("Part 6 · 实战项目篇",    range(25, 29)),
    ("Part 7 · 前沿与展望",    range(29, 31)),
]

MERMAID_RE = re.compile(
    r'<pre><code class="language-mermaid">(.*?)</code></pre>',
    re.DOTALL,
)
CHAPTER_H1_RE = re.compile(r"^#\s+Ch\d+\s*[｜|]\s*(.+?)\s*$", re.MULTILINE)


# ---------------------------------------------------------------------------
# 数据
# ---------------------------------------------------------------------------
@dataclass
class Chapter:
    number: int
    path: Path
    title: str
    clean_title: str
    body: str
    part: str = ""

    @property
    def slug(self) -> str:
        return f"ch{self.number:02d}"


def log(msg: str) -> None:
    print(f"[render_pdf] {msg}", flush=True)


def part_of(n: int) -> str:
    for name, rng in PART_RANGES:
        if n in rng:
            return name
    return ""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="将 agent-learn 项目章节渲染为 PDF（Playwright 后端）")
    p.add_argument("--chapters-dir", type=Path, default=DEFAULT_CHAPTERS_DIR)
    p.add_argument("--output", "-o", type=Path, default=DEFAULT_OUTPUT)
    p.add_argument("--meta", type=Path, default=DEFAULT_META)
    p.add_argument("--no-toc", action="store_true")
    p.add_argument("--no-cover", action="store_true")
    p.add_argument("--start", type=int, default=1)
    p.add_argument("--end", type=int, default=30)
    p.add_argument("--verbose", "-v", action="store_true")
    return p.parse_args()


# ---------------------------------------------------------------------------
# 章节收集
# ---------------------------------------------------------------------------
def collect_chapters(chapters_dir: Path, start: int, end: int) -> list[Chapter]:
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
        raise SystemExit(f"未在 {chapters_dir} 找到章节文件")
    return chapters


# ---------------------------------------------------------------------------
# Markdown → HTML
# ---------------------------------------------------------------------------
def md_to_html(md_text: str) -> str:
    return markdown.markdown(
        md_text,
        extensions=[
            "fenced_code", "tables", "attr_list", "def_list",
            "footnotes", "sane_lists", "smarty",
            TocExtension(toc_depth="2-3", anchorlink=False),
        ],
        output_format="html5",
    )


# ---------------------------------------------------------------------------
# Mermaid 占位
# ---------------------------------------------------------------------------
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


def replace_mermaid(html: str) -> str:
    def _repl(m: re.Match) -> str:
        src = (m.group(1).replace("&lt;", "<").replace("&gt;", ">")
                .replace("&amp;", "&").replace("&quot;", "\"")
                .replace("&#39;", "'"))
        return _mermaid_placeholder(src)
    return MERMAID_RE.sub(_repl, html)


# ---------------------------------------------------------------------------
# 目录
# ---------------------------------------------------------------------------
def build_toc_html(chapters: list[Chapter],
                   rendered: list[tuple[Chapter, str]]) -> str:
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
    css = CSS_PATH.read_text(encoding="utf-8") if CSS_PATH.exists() else ""

    # Add additional CSS for Chromium PDF rendering
    chromium_css = """
@page {
  size: A4;
  margin: 2.6cm 2.2cm 2.8cm 2.2cm;
}

@page cover_page {
  size: A4;
  margin: 0;
}

.cover {
  page: cover_page;
  width: 210mm;
  height: 297mm;
  box-sizing: border-box;
  page-break-after: always;
}

.toc {
  page-break-after: always;
}

.chapter {
  page-break-before: always;
}

h1 {
  page-break-before: always;
}

.chapter > h1:first-child {
  page-break-before: avoid;
}

table, figure, pre, .mermaid-placeholder, .mermaid-figure,
blockquote, .callout {
  page-break-inside: avoid;
}
h1, h2, h3, h4, h5, h6 {
  page-break-after: avoid;
}
"""

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
{chromium_css}
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

    # 3. 渲染 Markdown → HTML
    rendered: list[tuple[Chapter, str]] = []
    for ch in chapters:
        log(f"  · {ch.slug}  {ch.title}")
        html = md_to_html(ch.body)
        html = replace_mermaid(html)
        rendered.append((ch, html))

    # 4. 拼装 HTML
    log("拼装 HTML 文档（封面 + 目录 + 正文）")
    html_doc = build_html(
        chapters, rendered, meta,
        include_toc=not args.no_toc,
        include_cover=not args.no_cover,
    )

    # 5. Playwright 渲染
    args.output.parent.mkdir(parents=True, exist_ok=True)
    log(f"开始渲染 PDF → {args.output}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_content(html_doc, wait_until="networkidle")
        # Wait for fonts/rendering to settle
        page.wait_for_timeout(2000)
        page.pdf(
            path=str(args.output),
            format="A4",
            margin={"top": "2.6cm", "right": "2.2cm", "bottom": "2.8cm", "left": "2.2cm"},
            print_background=True,
            display_header_footer=False,
        )
        browser.close()

    # 6. 报告
    if args.output.exists():
        size_mb = args.output.stat().st_size / 1024 / 1024
        log(f"✅ 完成：{args.output}  ({size_mb:.1f} MB)")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
