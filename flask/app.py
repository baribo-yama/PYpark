from flask import Flask, render_template
import subprocess
import os

app = Flask(__name__)

# main.pyの起動状態を管理
ad_process = None

def start_ad_system():
    """annoying_ad/main.pyを起動する関数"""
    global ad_process

    # すでに起動中でプロセスがまだ生きている場合は起動しない
    if ad_process is not None and ad_process.poll() is None:
        return

    # main.pyのパスを取得
    # app.pyのディレクトリから見た相対パス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    print(current_dir)
    parent_dir = os.path.dirname(current_dir)
    print(parent_dir)
    main_py_path = os.path.join(parent_dir, "annoying_ad", "main.py")

    # main.pyをバックグラウンドで起動
    ad_process = subprocess.Popen(
        ["python", main_py_path],
        cwd=os.path.join(parent_dir, "annoying_ad")
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/carousel1")
def carousel1():
    start_ad_system()
    return render_template("carousel1.html")

@app.route("/carousel2")
def carousel2():
    start_ad_system()
    return render_template("carousel2.html")

@app.route("/carousel3")
def carousel3():
    start_ad_system()
    return render_template("carousel3.html")

@app.route("/carousel4")
def carousel4():
    start_ad_system()
    return render_template("carousel4.html")

@app.route("/carousel5")
def carousel5():
    start_ad_system()
    return render_template("carousel5.html")

@app.route("/carousel6")
def carousel6():
    start_ad_system()
    return render_template("carousel6.html")

@app.route("/carousel7")
def carousel7():
    start_ad_system()
    return render_template("carousel7.html")

@app.route("/carousel8")
def carousel8():
    start_ad_system()
    return render_template("carousel8.html")

if __name__ == "__main__":
    app.run(debug=True)
