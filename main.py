from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

# 配置文件和模板目录的路径
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

# 读取配置 (不再进行任何排序)
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

book_names = config["book_config"]
entries = config["entries"]


def ensure_template(book, unit, name):
    """
    如果模板文件不存在，则自动创建它。
    """
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


@app.route("/")
def index():
    """
    主页路由，按 config.json 的顺序生成目录。
    """
    grouped = {}
    for book_code, unit, name in entries:
        display_name = book_names.get(book_code, book_code)
        # setdefault 会按遇到的顺序添加新键，从而保持顺序
        grouped.setdefault(display_name, []).append(
            {"unit": unit, "name": name, "template": ensure_template(book_code, unit, name)}
        )
    
    # 直接使用 grouped.items()，它会保持插入顺序
    # 不再需要 sorted() 函数进行排序
    return render_template("index.html", grouped=grouped.items())


@app.route("/view/<template>")
def view(template):
    path = os.path.join(TEMPLATE_DIR, template)
    if not os.path.exists(path):
        abort(404)
    return render_template(template)


@app.route('/favicon.ico')
def favicon():
    return ('', 204)


if __name__ == "__main__":
    # 按照您的建议，在启动前可以先运行 format.py
    # 例如在 shell 中: python format.py && uv run python main.py
    app.run(debug=True, host="::", port=6400)