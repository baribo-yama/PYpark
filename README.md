# Hand Distance

このスクリプトは MediaPipe Tasks API の HandLandmarker を使って、カメラから手を検出し、2つの手の中心間のピクセル距離を表示します。

準備

1. Python 3.8+ を推奨
2. 依存をインストール:

```bash
pip install -r requirements.txt
```

実行

```bash
python hands_distance.py
```

注意

- 初回実行時に `hand_landmarker.task` モデルファイルが存在しないと、自動ダウンロードを試みます。ネットワークに接続されていない場合は手動でモデルをダウンロードしてスクリプトと同じディレクトリに置いてください。
- Windows ではカメラデバイスの接続やドライバに依存します。もしカメラが開けない場合は、`hands_distance.py` を編集して別のカメラインデックス（0,1,...）を試してください。
