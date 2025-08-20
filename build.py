import os
import json
from flask import Flask, render_template

app = Flask(__name__, template_folder="templates", static_folder="static")

# 读取 config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

book_names = config["book_config"]
entries = config["entries"]

BUILD_DIR = "build"
os.makedirs(BUILD_DIR, exist_ok=True)

# ---- 新增：路径适配脚本 ----
PATH_ADAPTER_SCRIPT = """
<script>
    // 自动适配 GitHub Pages 子路径和自定义域名
    const isGithubPath = window.location.hostname.includes('github.io');
    const base = document.createElement('base');
    base.href = isGithubPath ? '/math/' : '/';
    document.head.appendChild(base);
</script>
"""

# ---- 修改后的 HTML 处理函数 ----
def process_html(html):
    """在所有 HTML 文件的 <head> 标签后插入路径适配脚本"""
    head_close = html.find('</head>')
    if head_close != -1:
        return html[:head_close] + PATH_ADAPTER_SCRIPT + html[head_close:]
    return html  # 如果没有找到 head 标签，原样返回

# ---- 覆盖 url_for ----
def fake_url_for(endpoint, **values):
    if endpoint == "static":
        return f"/static/{values['filename']}"
    elif endpoint == "view":
        return f"/view/{values['template']}"
    elif endpoint == "index":
        return f"/index.html"
    else:
        raise RuntimeError(f"Unsupported endpoint: {endpoint}")

app.jinja_env.globals["url_for"] = fake_url_for

app.jinja_env.globals["url_for"] = fake_url_for

# ---- 辅助：确保模板文件存在 ----
TEMPLATE_DIR = "templates"
def ensure_template(book, unit, name):
    filename = f"{book}_{unit.replace('.', '_')}.html"
    path = os.path.join(TEMPLATE_DIR, filename)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"""{{% extends "base.html" %}}

{{% block title %}}{name}｜{book_names.get(book, book)}{{% endblock %}}

{{% block content %}}
<div class="chapter-content">
  <h2>{name}</h2>
  <p>这里是章节内容占位。</p>
</div>
{{% endblock %}}
""")
    return filename

# ---- 构建 index.html ----
def build_index():
    grouped = {}
    for book, unit, name in entries:
        display_name = book_names.get(book, book)
        grouped.setdefault(display_name, []).append(
            {
                "unit": unit,
                "name": name,
                "template": ensure_template(book, unit, name)
            }
        )

    with app.app_context():
        html = render_template("index.html", grouped=grouped.items())
    
    # 处理 HTML 并写入
    with open(os.path.join(BUILD_DIR, "index.html"), "w", encoding="utf-8") as f:
        f.write(process_html(html))

# ---- 构建章节页面 ----
def build_chapters():
    out_dir = os.path.join(BUILD_DIR, "view")
    os.makedirs(out_dir, exist_ok=True)
    for book, unit, name in entries:
        template = f"{book}_{unit.replace('.', '_')}.html"
        with app.app_context():
            html = render_template(template)
        out_path = os.path.join(out_dir, template)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(process_html(html))

if __name__ == "__main__":
    print("Building static site...")
    build_index()
    build_chapters()
    print(f"✅ Done! HTML in {BUILD_DIR}/ (已自动添加路径适配脚本)")