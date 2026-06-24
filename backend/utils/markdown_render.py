"""Markdown 渲染 + HTML 清洗工具。"""

from __future__ import annotations

import markdown
import bleach

# bleach 允许的标签和属性白名单
ALLOWED_TAGS: list[str] = [
    "h1", "h2", "h3", "h4", "h5", "h6",
    "p", "br", "hr",
    "blockquote", "pre", "code",
    "ul", "ol", "li",
    "a", "img",
    "strong", "em", "del", "sup", "sub",
    "table", "thead", "tbody", "tr", "th", "td",
    "input",  # checkbox in task lists
]

ALLOWED_ATTRIBUTES: dict[str, list[str]] = {
    "a": ["href", "title", "target", "rel"],
    "img": ["src", "alt", "title", "width", "height"],
    "td": ["align"],
    "th": ["align"],
    "code": ["class"],  # 语法高亮 class
    "input": ["type", "checked", "disabled"],
}

# Markdown 扩展
_MD_EXTENSIONS: list[str] = [
    "fenced_code",
    "tables",
    "toc",
    "nl2br",
    "sane_lists",
    "codehilite",
    "md_in_html",
]


def render_markdown(md_text: str) -> str:
    """将 Markdown 文本渲染为安全的 HTML。

    流程：Markdown → HTML → bleach 清洗（防 XSS）。
    """
    if not md_text:
        return ""

    html = markdown.markdown(
        md_text,
        extensions=_MD_EXTENSIONS,
        output_format="html",
    )

    cleaned = bleach.clean(
        html,
        tags=ALLOWED_TAGS,
        attributes=ALLOWED_ATTRIBUTES,
        strip=True,
    )

    # 为外部链接补 rel="noopener noreferrer"
    cleaned = bleach.linkify(
        cleaned,
        callbacks=[
            lambda attrs, new: (
                attrs.update({"rel": "noopener noreferrer"}) if new else attrs
            ) or attrs
        ],
        skip_tags=["code", "pre"],
    )

    return cleaned
