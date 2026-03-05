import cv2
import random
import os


class AdObject:
    # start_posはstart positionのことか？
    def __init__(self, start_pos):
        self.x, self.y = start_pos
        self.state = "coming"
        self.speed = 0.08  # 係数8パーセント
        self.offset_x = random.randint(-50, 50)
        self.offset_y = random.randint(-50, 50)

        # デバッグ：現在のディレクトリと画像ファイルの存在確認
        print(f"現在のディレクトリ: {os.getcwd()}")
        print(f"imgフォルダの存在: {os.path.exists('img')}")

        # 画像を読み込み（相対パスを修正）
        img_files = ["img1.jpg", "img2.jpg", "img3.jpg", "img4.jpg", "img5.jpg", "img6.jpg", "img7.jpg", "img8.jpg"]
        selected_img = random.choice(img_files)
        # 現在のスクリプトファイルの位置を基準にパスを構築
        script_dir = os.path.dirname(os.path.abspath(__file__))
        img_path = os.path.join(script_dir, "img", selected_img)

        print(f"選択された画像: {selected_img}")
        print(f"スクリプトディレクトリ: {script_dir}")
        print(f"画像パス: {img_path}")
        print(f"ファイルの存在: {os.path.exists(img_path)}")

        self.image = cv2.imread(img_path)

        if self.image is not None:
            print("画像読み込み成功")
            # 画像のサイズを調整（90×50ピクセルに変更）
            self.image = cv2.resize(self.image, (270, 150))
            self.img_height, self.img_width = self.image.shape[:2]
        else:
            print("画像読み込み失敗 - フォールバック使用")
            # 画像が読み込めない場合はnoneのまま
            self.img_width, self.img_height = 90, 50

    def update(self, target, swipe_detected):
        if self.state == "coming":
            self.x += (target[0] - self.x) * self.speed
            self.y += (target[1] - self.y) * self.speed
            if swipe_detected:
                self.state = "blocked"

        elif self.state == "blocked":
            self.x += 40
            if self.x < -300:
                self.state = "remove"  # removeどこで定義してる？

    # 表示させるオブジェクトの定義
    # def draw(self, frame):
    #     if self.state in ("coming", "blocked"):
    #         cv2.rectangle(
    #             frame,
    #             (int(self.x) - 40, int(self.y) - 25),
    #             (int(self.x) + 40, int(self.y) + 25),
    #             (0, 0, 255),
    #             2,
    #         )

    def draw(self, frame):
        if self.state in ("coming", "blocked"):
            if self.image is not None:
                # 単純に現在位置(self.x, self.y)で画像を描画
                x1 = int(self.x) - (self.img_width // 2) + self.offset_x
                y1 = int(self.y) - (self.img_height // 2) + self.offset_y
                x2 = x1 + self.img_width
                y2 = y1 + self.img_height

                # 境界チェック（画面外にオブジェクトが出ないようにチェックする）
                if x1 >= 0 and y1 >= 0 and x2 <= frame.shape[1] and y2 <= frame.shape[0]:
                    frame[y1:y2, x1:x2] = self.image
            else:
                # 元の矩形描画（フォールバック）
                cv2.rectangle(
                    frame,
                    (int(self.x) - 40, int(self.y) - 25),
                    (int(self.x) + 40, int(self.y) + 25),
                    (0, 0, 255),
                    2,
                )



def random_start(w, h):
    positions = [
        (-200, h // 2),
        (w + 200, h // 2),
        (w // 2, -200),
        (w // 2, h + 200),
        (-200, -200),
        (w + 200, -200),
        (-200, h + 200),
        (w + 200, h + 200),
    ]
    return random.choice(positions)
