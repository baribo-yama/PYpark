import cv2
import os
import time
from PIL import ImageOps
from PIL import Image
import mediapipe as mp
import numpy as np
from utils import Func05_pil2opencv, Func08_overlay_PILimage_alpha

class Headgear:
    def __init__(self, image_path, position=(0, 0), scale=1.0, rotation_speed = 0.0):
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

    def _touch_left_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        lx = self.pos[0] - self.width / 2
        within_x = abs(hand_xy[0] - lx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y

    def _touch_right_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        rx = self.pos[0] + self.width / 2
        within_x = abs(hand_xy[0] - rx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y

    def update(self, head_xy, right_xy, left_xy):
        
        touching_left  = self._touch_left_edge(left_xy)
        touching_right = self._touch_right_edge(right_xy)

        #print(f"Touching Left: {touching_left}, Right: {touching_right}")
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
    def __init__(self, image_path, position=(0, 0), scale=1.0, rotation_speed = 0.0):
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

    def _touch_left_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        lx = self.pos[0] - self.width / 2
        within_x = abs(hand_xy[0] - lx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y

    def _touch_right_edge(self, hand_xy, margin=50):
        if hand_xy is None:
            return False
        rx = self.pos[0] + self.width / 2
        within_x = abs(hand_xy[0] - rx) <= margin
        within_y = abs(hand_xy[1] - self.pos[1]) <= self.height / 2 + margin
        return within_x and within_y

    def update(self, head_xy, right_xy, left_xy):
        
        touching_left  = self._touch_left_edge(left_xy)
        touching_right = self._touch_right_edge(right_xy)

        print(f"Touching Left: {touching_left}, Right: {touching_right}")
        if head_xy is not None and self.is_touch(head_xy, ratio=0.5):
                self.set_position(head_xy)
                print("顔タッチ")
        elif touching_left and touching_right:
            # ここで好きな手の座標を使って位置更新。例えば頭に吸い付けるなら head_xy。
            if right_xy is not None and left_xy is not None:
                mid = (right_xy + left_xy) / 2.0
                self.set_position(mid)
                print("両手タッチ")

    # 脱ぐボタンの当たり判定
    def _is_inside(self, x, y):
        """ 現在の画像範囲に座標(x, y)があるかを判定 """
        img_x, img_y = self.pos
        w, h = self.width, self.height
        return (img_x <= x <= img_x + w) and (img_y <= y <= img_y + h)

# カメラセットアップ
cap = cv2.VideoCapture(0, cv2.CAP_MSMF)
cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
cap.set(cv2.CAP_PROP_FPS, 60)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 5500)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 8500)

# ポーズの位置取り用意
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()
mp_draw = mp.solutions.drawing_utils

# 画像を表示
follow = Headgear(".\\Image\\kutipatti.png", position=(1000, 300), scale=1.0)
remove = Button(".\\Image\\reset.png", position=(100, 100), scale=0.05 , rotation_speed = 0.0)

# 処理開始
while True:
    ret, frame = cap.read()
    if not ret:
        print("フレーム取得に失敗しました。")
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    frame_rgb = cv2.flip(frame_rgb, 1)
    results = pose.process(frame_rgb)
    h, w, _ = frame.shape

    if results.pose_landmarks:
        mp_draw.draw_landmarks(frame_rgb, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        Head = results.pose_landmarks.landmark[0]
        Right = results.pose_landmarks.landmark[17]
        Left = results.pose_landmarks.landmark[16]
        Reset_Right = results.pose_landmarks.landmark[19]
        Reset_Left = results.pose_landmarks.landmark[20]
        
        x = int(Head.x * w)
        y = int(Head.y * h)
        head_xy = np.array([x, y])
        x = int(Right.x * w)
        y = int(Right.y * h)
        righthand_xy = np.array([x, y])
        x = int(Left.x * w)
        y = int(Left.y * h)
        lefthand_xy = np.array([x, y])
        follow.update(head_xy,righthand_xy,lefthand_xy)
        x = int(Reset_Right.x * w)
        y = int(Reset_Right.y * h)
        Reset_Right_xy = np.array([x, y])
        x = int(Reset_Left.x * w)
        y = int(Reset_Left.y * h)
        Reset_Left_xy = np.array([x, y])

    hit_right = remove.is_touch(Reset_Right_xy,ratio=2.0)
    hit_left = remove.is_touch(Reset_Left_xy,ratio=2.0)
    print(f"Hit Left: {hit_left}, Right: {hit_right}")
    
    if hit_right or hit_left:
        print("脱ぐボタンタッチ")
        follow.set_position((1000,300))  # 元の位置に戻す
        
    # キャラ描画は毎フレーム
    image = cv2.cvtColor(frame_rgb, cv2.COLOR_BGR2RGB)
    frame_PIL = Image.fromarray(image)
    frame_PIL_Draw = follow.draw(frame_PIL)

    #脱ぐボタンを描画 固定
    frame_PIL_Draw = remove.draw(frame_PIL_Draw)

    frame_cv = Func05_pil2opencv(frame_PIL_Draw)
    
    cv2.imshow("Hand Ball Interaction", frame_cv)
    if cv2.waitKey(1) & 0xFF == 27:
        break

cap.release()
cv2.destroyAllWindows()
