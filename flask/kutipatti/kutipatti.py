import cv2               #OpenCV:カメラ映像の取得や表示に使用
import os                #ファイルパスの確認などに使用
from PIL import Image    #Pillow:画像の読み込みや合成に使用
import mediapipe as mp   #MediaPipe:骨格検出(Pose)に使用
import numpy as np       #数値計算(距離計算や座標扱い)に使用
from utils import Func05_pil2opencv, Func08_overlay_PILimage_alpha

class Headgear:
    #画像の読み込み、指定されたサイズにリサイズ、画像の大きさを元に「当たり判定の半径」を計算
    def __init__(self, image_path, position=(0, 0), scale=1.0, rotation_speed = 0.0):
        #画像ファイルが存在するか確認。なければエラーを返す
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"画像が見つからなかった: {image_path}")
        #画像を読み込み、RGBAモードに変換
        self.original_img = Image.open(image_path).convert("RGBA")
        #画像の幅と高さを取得
        w, h = self.original_img.size
        #画像の大きさを指定された倍率でリサイズし、self.imgに保存
        self.img = self.original_img.resize((int(w * scale), int(h * scale)))
        #リサイズ後のサイズを保存
        self.width, self.height = self.img.size
        
        # 現在の動作モード
        self.mode = "follow"
        # 初期位置をnumpy配列として保存
        self.initial_pos = np.array(position, dtype=np.float32)
        self.pos = self.initial_pos.copy()
        self.radius = max(self.width, self.height) / 2  # 当たり判定半径
        
    # キャラクターの中心座標を更新
    def set_position(self, point):
        self.pos = np.array(point, dtype=np.float32)
    
    # 現在の座標を中心に、画像を背景に重ねる
    def draw(self, pil_frame):
        cx, cy = self.pos
        x = int(cx - self.width / 2)
        y = int(cy - self.height / 2)
        result = Func08_overlay_PILimage_alpha(pil_frame, self.img, (x, y))
        return result

    # 指定された点と自分の位置との「距離」を計算し、当たり判定の範囲内かどうかを返す
    def is_touch(self, point, ratio=1.0):
        dist = np.linalg.norm(self.pos - point)
        return dist < self.radius * ratio

    #　手が画像の「左端」や「右端」付近にあるかを判定する関数、左手
    def _touch_left_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        lx = self.pos[0] - self.width / 2
        within_x = abs(hand_xy[0] - lx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y
    #　手が画像の「左端」や「右端」付近にあるかを判定する関数、右手
    def _touch_right_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        rx = self.pos[0] + self.width / 2
        within_x = abs(hand_xy[0] - rx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y

    # 頭がキャラクターに触れたら、頭の位置に吸着する、左右の手がキャラクターの両端に触れていたら、両手の中間地点に移動する
    def update(self, head_xy, right_xy, left_xy):
        
        touching_left  = self._touch_left_edge(left_xy)
        touching_right = self._touch_right_edge(right_xy)

        if head_xy is not None and self.is_touch(head_xy, ratio=0.5):
                self.set_position(head_xy)
                print("顔タッチ")
        elif touching_left and touching_right:
            # ここで好きな手の座標を使って位置更新。例えば頭に吸い付けるなら head_xy。
            if right_xy is not None and left_xy is not None:
                mid = (right_xy + left_xy) / 2.0
                self.set_position(mid)
                print("両手タッチ") 

class Button:
    def __init__(self, image_path, position=(0, 0), scale=2.0, rotation_speed = 0.0):
        if not os.path.exists(image_path):
            raise FileNotFoundError(f"Image not found: {image_path}")
        self.original_img = Image.open(image_path).convert("RGBA")
        w, h = self.original_img.size
        self.img = self.original_img.resize((int(w * scale), int(h * scale)))
        self.width, self.height = self.img.size
        
        self.mode = "follow"
        self.initial_pos = np.array(position, dtype=np.float32)
        self.pos = self.initial_pos.copy()
        self.radius = max(self.width, self.height) / 2  # 当たり判定半径
        
    def set_position(self, point):
        self.pos = np.array(point, dtype=np.float32)

    def draw(self, pil_frame):
        cx, cy = self.pos
        x = int(cx - self.width / 2)
        y = int(cy - self.height / 2)
        result = Func08_overlay_PILimage_alpha(pil_frame, self.img, (x, y))
        return result

    def is_touch(self, point, ratio=1.0):
        dist = np.linalg.norm(self.pos - point)
        return dist < self.radius * ratio

# カメラセットアップ
cap = cv2.VideoCapture(0, cv2.CAP_MSMF) #カメラ起動

# ポーズの位置取り用意
mp_pose = mp.solutions.pose
pose = mp_pose.Pose() # 骨格検出エンジンの起動
mp_draw = mp.solutions.drawing_utils

# 画像を表示
follow = Headgear(".\\Image\\kutipatti.png", position=(310, 425), scale=0.5)                 #キャラクターの画像を読み込みと出現させる位置の設定
remove = Button(".\\Image\\reset.png", position=(50, 50), scale=0.05 , rotation_speed = 0.0)#リセットの画像を読み込みと出現させる位置の設定

# 処理開始
while True:
    ret, frame = cap.read()                 #カメラから1フレーム読み込む
    if not ret:                             #読み込めなかったら終了
        print("フレーム取得に失敗しました。")
        break

    frame_rgb = cv2.flip(frame, 1)          #画面を鏡のように左右反転させる
    results = pose.process(frame_rgb)       #MediaPipeで骨格解析を実行
    h, w, _ = frame.shape                   #画面の縦横のサイズを取得（座標計算用）

    hit_right = False
    hit_left = False

    if results.pose_landmarks:
        #ランドマーク（体の各部位）の座標を取得
        Head = results.pose_landmarks.landmark[0]        #鼻
        Right = results.pose_landmarks.landmark[17]      #右手首
        Left = results.pose_landmarks.landmark[16]       #左手首
        Reset_Right = results.pose_landmarks.landmark[19]#右の掌の中指の付け根
        Reset_Left = results.pose_landmarks.landmark[20] #左の掌の中指の付け根

        # 座標変換（0~1の数値を画面のピクセル座標x,yに変換）
        x = int(Head.x * w)
        y = int(Head.y * h)
        head_xy = np.array([x, y])
        x = int(Right.x * w)
        y = int(Right.y * h)
        righthand_xy = np.array([x, y])
        x = int(Left.x * w)
        y = int(Left.y * h)
        lefthand_xy = np.array([x, y])
        # キャラクターの位置更新ロジックを実行　頭や手の位置を渡して吸着するか移動するかを判断させる
        follow.update(head_xy,righthand_xy,lefthand_xy)
        x = int(Reset_Right.x * w)
        y = int(Reset_Right.y * h)
        Reset_Right_xy = np.array([x, y])
        x = int(Reset_Left.x * w)
        y = int(Reset_Left.y * h)
        Reset_Left_xy = np.array([x, y])
        
        # resetボタンの判定　指先がボタンに触れたかチェック
        hit_right = remove.is_touch(Reset_Right_xy,ratio=2.0)
        hit_left = remove.is_touch(Reset_Left_xy,ratio=2.0)
        print(f"Hit Left: {hit_left}, Right: {hit_right}")
    
    # どちらかの手がリセットボタンに触れたらキャラクターの位置を初期位置に強制移動
    if hit_right or hit_left:
        print("脱ぐボタンタッチ")
        follow.set_position((310,425))  # 元の位置に戻す
        
    # キャラ描画は毎フレーム
    image = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB) # OpenCV形式からPIL形式に変換
    frame_PIL = Image.fromarray(image)
    #キャラクターを描画
    frame_PIL_Draw = follow.draw(frame_PIL)

    #脱ぐボタンを描画
    frame_PIL_Draw = remove.draw(frame_PIL_Draw)
    #脱ぐボタンを表示するためにPIL形式からOpenCV形式に戻す
    frame_cv = Func05_pil2opencv(frame_PIL_Draw)
    
    # ウェインドウ作成と表示
    window_name = "kutipatti"
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.imshow(window_name, frame_cv) #画面表示
    # ESCキー(27)が押されたらループを抜ける
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
