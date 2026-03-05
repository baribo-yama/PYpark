from flask import Flask, render_template
import subprocess
import os

# from kutipatti import kutipatti, utils

app = Flask(__name__)

# main.pyの起動状態を管理
ad_process = None
kutipatti_process = None
ascii_process = None

# 広告スイーパー起動関数
def start_ad_system():
    """annoying_ad/main.pyを起動する関数"""
    global ad_process

    # すでに起動中でプロセスがまだ生きている場合は起動しない
    # 早期リターンてやつ？returnするとそれより下の関数のコードは実行されずに関数を終了する
    if ad_process is not None and ad_process.poll() is None:
        return

    # main.pyのパスを取得
    # app.pyのディレクトリから見た相対パス
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(current_dir, "annoying_ad", "main.py")

    # main.pyをバックグラウンドで起動
    # cwdはcurrent workng directory　作業ディレクトリを指定する
    ad_process = subprocess.Popen(
        ["python", main_py_path],
        cwd=os.path.join(current_dir, "annoying_ad")
    )

# ascii起動関数
def start_kutipatti():
    global kutipatti_process

    if kutipatti_process is not None and kutipatti_process.poll() is None:
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(current_dir, "kutipatti", "kutipatti.py")

    kutipatti_process = subprocess.Popen(
        ["python", main_py_path],
        cwd=os.path.join(current_dir, "kutipatti")
    )

# ascii起動関数
def start_ascii():
    global ascii_process

    if ascii_process is not None and ascii_process.poll() is None:
        return

    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_py_path = os.path.join(current_dir, "ascii", "test_ascii.py")

    _process = subprocess.Popen(
        ["python", main_py_path],
        cwd=os.path.join(current_dir, "ascii")
    )

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/carousel1")
def carousel1():

    return render_template("carousel1.html")

@app.route("/carousel2")
def carousel2():

    return render_template("carousel2.html")

@app.route("/carousel3")
def carousel3():

    return render_template("carousel3.html")

@app.route("/carousel4")
def carousel4():
    start_ad_system()
    return render_template("carousel4.html")

# スタートボタンでシステムを起動する場合
# @app.route("/ad_button_click")
# def start():
#     start_ad_system()
#     return ("", 204)

@app.route("/carousel5")
def carousel5():
    start_kutipatti()
    return render_template("carousel5.html")


@app.route("/carousel6")
def carousel6():
    start_ascii()
    return render_template("carousel6.html")

@app.route("/carousel7")
def carousel7():

    return render_template("carousel7.html")

@app.route("/carousel8")
def carousel8():

    return render_template("carousel8.html")

if __name__ == "__main__":
    app.run(debug=True)
