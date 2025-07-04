from flask import Flask, render_template, abort
import os
import json

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")
TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")

with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = json.load(f)

book_names = config["book_config"]
entries = config["entries"]


def sort_key(entry):
    book_code, unit_code, _ = entry
    # 先按书籍：必修(b) 在前，选修(x) 在后
    order_book = 0 if book_code.startswith("b") else 1
    # 再按章节号数值排序：3.4 < 3.10
    major, *minor = map(int, unit_code.split("."))
    minor_val = minor[0] if minor else 0
    return (order_book, int(book_code[1:]), major, minor_val)


entries.sort(key=sort_key)


# 自动创建模板文件
def ensure_template(book, unit, name):
    filename = f"{book}_{unit.replace('.', '_')}.html"
    path = os.path.join(TEMPLATE_DIR, filename)
    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"""{{% extends "base.html" %}}

{{% block title %}}{name}｜{book_names.get(book, book)}{{% endblock %}}

{{% block content %}}
<h2>{name}</h2>
<p>这里是章节内容占位。</p>
{{% endblock %}}
""")
    return filename


@app.route("/")
def index():
    grouped = {}
    for book, unit, name in entries:
        display_name = book_names.get(book, book)
        grouped.setdefault(display_name, []).append(
            {"unit": unit, "name": name, "template": ensure_template(book, unit, name)}
        )
    # 按书顺序排列
    sorted_books = sorted(
        grouped.items(), key=lambda kv: (0 if "必修" in kv[0] else 1, kv[0])
    )
    return render_template("index.html", grouped=sorted_books)


@app.route("/view/<template>")
def view(template):
    path = os.path.join(TEMPLATE_DIR, template)
    if not os.path.exists(path):
        abort(404)
    return render_template(template)

@app.route('/favicon.ico')
def favicon():
    # 直接返回一个 204 No Content 响应，告诉浏览器这里没有图标。
    return ('', 204)

if __name__ == "__main__":
    app.run(debug=True, host="::", port=6400)
