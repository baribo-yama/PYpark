from PIL import Image
import cv2
import numpy as np
import random
import os

#指定した閾値以上のRGB値を持つピクセルのアルファ値を0にする
def Func01_ImageAlpha(image, threshold=200):
    image = image.convert('RGBA')
    size = image.size
    image_dst = Image.new('RGBA', size)
    for x in range(size[0]):
        for y in range(size[1]):
            r, g, b, a = image.getpixel((x, y))
            if r >= threshold and g >= threshold and b >= threshold:
                a = 0
            else:
                a = 255
            image_dst.putpixel((x, y), (r, g, b, a))
    return image_dst

#指定した座標に画像を合成する
def Func02_ImageAdd(image_src, image_add, x, y):
    image_dst = image_src.copy()
    image_dst.paste(image_add, (x, y), image_add)
    return image_dst



#白＝255, 黒=0の画像を作成し、指定した閾値以下の色は黒にする、それ以外は白
def Func03_ImageMask(image, threshold=200):
    image = image.convert('RGBA')
    size = image.size
    image_dst = Image.new('RGBA', size)
    for x in range(size[0]):
        for y in range(size[1]):
            r, g, b, a = image.getpixel((x, y))
            gray = (0.299*r) + (0.587*g) + (0.114 * b)

            if gray <= threshold:
                a = 0 #黒
            else:
                a = 255 #白
            image_dst.putpixel((x, y), (a, a, a, 255))
    return image_dst.convert("L")


### OpenCV型 => PIL型　の変換関数
def Func04_opencv2pil(in_image):
    new_image = in_image.copy() #複製
    if new_image.ndim == 2:
        pass
    elif new_image.shape[2] == 3:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2RGB)
    elif new_image.shape[2] == 4:
        new_image = cv2.cvtColor(new_image, cv2.COLOR_BGRA2RGBA)
    else:
        return None
    new_image = Image.fromarray(new_image)
    return new_image

### PIL型 => OpenCV型　の変換関数
def Func05_pil2opencv(in_image):
    out_image = np.array(in_image, dtype=np.uint8)
    if out_image.ndim == 2:
        pass
    elif out_image.shape[2] == 3:
        out_image = cv2.cvtColor(out_image, cv2.COLOR_RGB2BGR)
    elif out_image.shape[2] == 4:
        out_image = cv2.cvtColor(out_image, cv2.COLOR_RGBA2BGR)
    
    return out_image

#白＝255, 黒=0の画像を作成し、指定した閾値以下の色は黒にする、それ以外は白
def Func06_ImageMask(image, threshold=200):
    image = image.convert('RGBA')
    size = image.size
    image_dst = Image.new('RGBA', size)
    for x in range(size[0]):
        for y in range(size[1]):
            r, g, b, a = image.getpixel((x, y))
            gray = (0.299*r) + (0.587*g) + (0.114 * b)

            if gray <= threshold:
                a = 255 #白
            else:
                a = 0 #黒
            image_dst.putpixel((x, y), (a, a, a, 255))
    return image_dst.convert("L")

#背景に透明画像を貼り付ける
def Func07_overlay_CVimage_alpha(img, img_overlay, pos):
    """  
    OpenCV画像上にPillow画像（透過有）をアルファ合成する
    img: OpenCV BGR ndarray (H,W,3)
    img_overlay: Pillow RGBA画像
    pos: 合成位置 (x,y) 左上座標
    return: 合成後のOpenCV BGR ndarray
    """
    x, y = pos
    overlay = np.array(img_overlay)
    h, w = overlay.shape[:2]

    # OpenCV画像をRGBAに変換（透明度なしでalpha=255に）
    img_pil = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB)).convert("RGBA")

    # 透明なキャンバスを作り、合成対象画像を指定位置に貼る
    tmp = Image.new("RGBA", img_pil.size, (0,0,0,0))
    tmp.paste(img_overlay, (x, y), img_overlay)

    # もとのフレームと透明キャンバスをアルファ合成
    combined = Image.alpha_composite(img_pil, tmp)

    # RGBA→BGR OpenCV用に変換
    return cv2.cvtColor(np.array(combined), cv2.COLOR_RGBA2BGR)

def Func08_overlay_PILimage_alpha(background_img: Image.Image, stamp_img: Image.Image, pos: tuple) -> Image.Image:
    """
    透明な画像を背景画像に合成する。
    背景・スタンプともに RGBA 想定。

    background_img: 背景（RGBA）
    stamp_img: 合成したい画像（透明を含むRGBA）
    pos: 貼り付け位置（左上）
    return: 合成後の画像（RGBA）
    """
    bg = background_img.convert("RGBA")
    stamp = stamp_img.convert("RGBA")
    
    # 透明なキャンバスにスタンプを貼る
    tmp = Image.new("RGBA", bg.size, (0, 0, 0, 0))
    tmp.paste(stamp, pos, mask=stamp)
    
    # 背景と合成
    result = Image.alpha_composite(bg, tmp)
    
    return result

#開始、終了位置をしているする 放物線に沿って移動するクラス
class C001_ParabolaMover:
    def __init__(self, startX, startY, endX, endY, max_step=1000, loop=True):
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY
        self.max_step = max_step
        self.loop = loop  # ループするかどうか
        self.step = 0
        self.currentX = startX
        self.currentY = startY

    def next_pos(self):
        if self.step > self.max_step:
            if self.loop:
                self.step = 0  # リセットしてループ
            else:
                return self.endX, self.endY

        t = self.step / self.max_step
        f_t = t ** 2

        self.currentX = int(self.startX + (self.endX - self.startX) * f_t)
        self.currentY = int(self.startY + (self.endY - self.startY) * f_t)

        self.step += 1
        return self.currentX, self.currentY

    def is_finished(self):
        return not self.loop and self.step > self.max_step
    

#サムネイル画像をグリッド状に合成するクラス、背景画像を設定できる
class C002_ImagePIL_GridComposer:
    global gImageBackGround # 背景画像のグローバル変数

    #初期化
    def __init__(self, canvas_width, canvas_height, thumb_width, thumb_height, bg_color=(255,255,255)):
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.thumb_width = thumb_width
        self.thumb_height = thumb_height
        self.bg_color = bg_color
        self.images = []

    # 背景画像を設定するメソッド
    def cange_background(self, image_pil):
        global gImageBackGround
        gImageBackGround = image_pil
    
    # 画像を追加するメソッド
    def add_imagePIL(self, img_pil):
        #サイズ変更
        img_pil = img_pil.resize((self.thumb_width, self.thumb_height), Image.LANCZOS)
        
        #追加しておく
        self.images.append(img_pil)
    
    # 画像を削除するメソッド
    def delete_images(self):
        self.images.clear()  # 画像リストを空にする

    # 画像パスリストを受け取り、Imageオブジェクトに変換して格納するメソッド
    ## 例：10枚の画像ファイルパスを渡す場合（上位）
    #image_paths = [f'img{i}.jpg' for i in range(1,11)]
    def add_images(self, image_paths):
        # 画像パスリストを受け取りImageオブジェクトに変換して格納
        for path in image_paths:
            img = Image.open(path)
            self.images.append(img)

    # 画像をグリッド状に合成するメソッド PIL画像を返す
    def compose(self):
        # 背景キャンバス作成
        canvas = Image.new('RGB', (self.canvas_width, self.canvas_height), self.bg_color)
        if gImageBackGround is not None:
            canvas.paste(gImageBackGround, (0, 0))  # 背景画像を貼り付け
        
        n = len(self.images)
        if n == 0:
            return canvas

        x = 0
        y = 0
        gap_x = 10  # 横方向の余白（画像間）
        gap_y = 10  # 縦方向の余白（行間）
        
        for img in self.images:
            # 画像をリサイズ
            thumb = img.resize((self.thumb_width, self.thumb_height), Image.LANCZOS)

            # 横幅オーバーなら改行
            if x + self.thumb_width > self.canvas_width:
                x = 0
                y += self.thumb_height + gap_y

            # 縦もオーバーするなら描画中止（or break）
            if y + self.thumb_height > self.canvas_height:
                print("Canvas overflow: image skipped.")
                break

            # 画像をキャンバスに貼り付け
            canvas.paste(thumb, (x, y))

            # 次の位置へ移動
            x += self.thumb_width + gap_x

        return canvas


class C003_Ball:
    def __init__(self, image_path, position=(0, 0), scale=1.0, mode="follow"):
        """
        Ballを画像で初期化
        :param image_path: PNG画像パス
        :param position: 初期位置（x, y）
        :param scale: 拡大縮小率
        :param mode: 'follow' または 'auto'
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        self.original_img = Image.open(image_path).convert("RGBA")
        w, h = self.original_img.size
        self.img = self.original_img.resize((int(w * scale), int(h * scale)))
        self.width, self.height = self.img.size

        self.pos = np.array(position, dtype=np.float32)
        self.radius = self.width // 2
        self.mode = mode  # 'follow' or 'auto'
        self.velocity = np.zeros(2, dtype=np.float32)
        self.move_timer = 0  # autoモードの移動時間カウント

    def set_position(self, pos):
        """ 位置をセット """
        self.pos = np.array(pos, dtype=np.float32)

    def is_touch(self, point):
        """ 接触判定 """
        dist = np.linalg.norm(self.pos - point)
        return dist < self.radius

    def is_collision(self, other_ball):
        """
        他のBallインスタンスとの衝突判定
        :param other_ball: Ballクラスのインスタンス
        :return: 衝突していればTrue
        """
        dist = np.linalg.norm(self.pos - other_ball.pos)
        return dist < (self.radius + other_ball.radius)

    def random_velocity(self, speed=10):
        """ ランダムな方向にベクトル生成 """
        angle = random.uniform(0, 2 * np.pi)
        return np.array([np.cos(angle), np.sin(angle)]) * speed

    def update(self, finger_tip_pos, frame_shape):
        """
        状態更新
        - mode: 'follow' → 指に追従
        - mode: 'auto' → 接触時に自動移動スタート
        """
        h, w = frame_shape[:2]

        if self.mode == "follow":
            if finger_tip_pos is not None and self.is_touch(finger_tip_pos):
                self.set_position(finger_tip_pos)

        elif self.mode == "auto":
            if self.move_timer > 0:
                # 移動継続
                self.pos += self.velocity
                self.move_timer -= 1

                # 壁にぶつかったら跳ね返る
                if self.pos[0] < self.radius or self.pos[0] > w - self.radius:
                    self.velocity[0] *= -1
                if self.pos[1] < self.radius or self.pos[1] > h - self.radius:
                    self.velocity[1] *= -1

            elif finger_tip_pos is not None and self.is_touch(finger_tip_pos):
                # 触れたらランダム移動開始（例: 3秒 ≒ 90フレーム）
                self.velocity = self.random_velocity()
                self.move_timer = 10  # 例: 10フレームで移動を止める

    def draw(self, cv2_frame, finger_tip_pos=None):
        """
        フレームに合成＋状態更新
        :param cv2_frame: OpenCVのBGRフレーム
        :param finger_tip_pos: 人差し指先の座標
        :return: 合成済みBGRフレーム
        """
        self.update(finger_tip_pos, cv2_frame.shape)

        # 合成位置（左上）
        x = int(self.pos[0] - self.width / 2)
        y = int(self.pos[1] - self.height / 2)

        result = Func07_overlay_CVimage_alpha(cv2_frame, self.img, (x, y))
        
        # OpenCV → PIL
        #frame_pil = Image.fromarray(cv2.cvtColor(cv2_frame, cv2.COLOR_BGR2RGB)).convert("RGBA")
        #frame_pil.alpha_composite(self.img, (x, y))
        # PIL → OpenCV
        # #result = cv2.cvtColor(np.array(frame_pil), cv2.COLOR_RGBA2BGR)
        
        
        return result

class C004_Cara:
    def __init__(self, image_path, position=(0, 0), scale=1.0):
        """
        Caraを画像で初期化
        :param image_path: PNG画像パス
        :param position: 初期位置（x, y）
        :param scale: 拡大縮小率
        """
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        self.original_img = Image.open(image_path).convert("RGBA")
        w, h = self.original_img.size
        self.img = self.original_img.resize((int(w * scale), int(h * scale)))
        self.width, self.height = self.img.size

        self.pos = np.array(position, dtype=np.float32)

    def update(self,pil_frame, multi_hand_landmarks):
        try:
            if not multi_hand_landmarks:
                print("手が検出されていません")
                return
            
            for hand_landmarks in multi_hand_landmarks:
                # 例：人差し指の先端（8番）の位置 画像内ならば 0 ～1の範囲
                index_tip = hand_landmarks.landmark[8]

                # 座標をピクセル単位に変換
                pixel_x = int(index_tip.x * pil_frame.width)
                pixel_y = int(index_tip.y *  pil_frame.height)
                print(f"人差し指先端: {pixel_x}, {pixel_y}")

                # 人差し指の先端座標を保存
                self.pos[0] = pixel_x
                self.pos[1] = pixel_y

                # 人差し指の各ランドマーク（番号は固定）
                mcp = hand_landmarks.landmark[5]   # 指の根本
                pip = hand_landmarks.landmark[6]   # 第1関節
                dip = hand_landmarks.landmark[7]   # 第2関節
                tip = hand_landmarks.landmark[8]   # 指先
                if tip.y < pip.y < mcp.y:
                    print("人差し指が立っている！")
                
        except Exception as e:
            print("処理中にエラー:", e)
    
    def draw(self, pil_frame, multi_hand_landmarks=None):
        if not multi_hand_landmarks:
            return pil_frame

        self.update(pil_frame,multi_hand_landmarks)

        # 合成位置（左上）
        x = int(self.pos[0] - self.width / 2)
        y = int(self.pos[1] - self.height / 2)

        result = Func08_overlay_PILimage_alpha(pil_frame, self.img, (x, y))
        
        return result
    

#ボール描画クラス
class BallSprite:
    def __init__(self, image, x, y, vx, vy, width=50, height=40):
        self.image = cv2.resize(np.array(image), (width, height))
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.width = width
        self.height = height

    def move(self, bounds_width, bounds_height):
        self.x += self.vx
        self.y += self.vy

        # 画面端で反射
        if self.x <= 0 or self.x + self.width >= bounds_width:
            self.vx *= -1
        if self.y <= 0 or self.y + self.height >= bounds_height:
            self.vy *= -1

    def check_collision(self, other):
        if (self.x < other.x + other.width and
            self.x + self.width > other.x and
            self.y < other.y + other.height and
            self.y + self.height > other.y):
            # ぶつかったら反転
            self.vx *= -1
            self.vy *= -1

    def add_sprite(self, x=None, y=None, vx=None, vy=None):
        """新しいボール（スプライト）を追加する関数"""
        pil_image = Image.open(self.sprite_path).convert("RGB")

        # ランダムな位置と速度（引数がNoneならランダム）
        x = x if x is not None else random.randint(0, self.width - 50)
        y = y if y is not None else random.randint(0, self.height - 40)
        vx = vx if vx is not None else random.choice([-5, 5])
        vy = vy if vy is not None else random.choice([-5, 5])

        sprite = BallSprite(pil_image, x, y, vx, vy)
        self.sprites.append(sprite)
    def draw(self, canvas):
        h, w, _ = canvas.shape

        # 描画エリアとの交差範囲を計算
        x1 = max(0, self.x)
        y1 = max(0, self.y)
        x2 = min(self.x + self.width, w)
        y2 = min(self.y + self.height, h)

        # 貼り付ける画像部分（元画像の切り出し範囲）
        img_x1 = max(0, -self.x)
        img_y1 = max(0, -self.y)
        img_x2 = img_x1 + (x2 - x1)
        img_y2 = img_y1 + (y2 - y1)

        if x1 < x2 and y1 < y2:  # 正常な範囲があれば描画
            canvas[y1:y2, x1:x2] = self.image[img_y1:img_y2, img_x1:img_x2]

class BounceSimulation:
    def __init__(self, bg_size=(1000, 800), sprite_path='sprite.png', sprite_count=10):
        self.width, self.height = bg_size
        self.sprites = []
        self.bg_color = (255, 255, 255)  # 白背景
        pil_image = Image.open(sprite_path).convert("RGB")

        for _ in range(sprite_count):
            x = random.randint(0, self.width - 50)
            y = random.randint(0, self.height - 40)
            vx = random.choice([-5, 5])
            vy = random.choice([-5, 5])
            sprite = BallSprite(pil_image, x, y, vx, vy)
            self.sprites.append(sprite)

    def update(self):
        for sprite in self.sprites:
            sprite.move(self.width, self.height)

        # 衝突判定（全ペアチェック）
        for i in range(len(self.sprites)):
            for j in range(i + 1, len(self.sprites)):
                self.sprites[i].check_collision(self.sprites[j])

    def render(self):
        canvas = np.ones((self.height, self.width, 3), dtype=np.uint8) * 255
        for sprite in self.sprites:
            sprite.draw(canvas)
        return canvas

    def run(self):
        while True:
            self.update()
            frame = self.render()
            cv2.imshow('Bounce Simulation', frame)
            if cv2.waitKey(30) == 27:  # ESCで終了
                break
        cv2.destroyAllWindows()