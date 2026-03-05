import cv2
import mediapipe as mp
import numpy as np  # 使ってない？


# Mediapipe 初期化
mp_face = mp.solutions.face_detection
mp_hands = mp.solutions.hands

cap = cv2.VideoCapture(0)

# 広告オブジェクトの状態
# ad_x, ad_yは広告オブジェクトの中心座標
ad_x, ad_y = -200, -200  # 初期位置（画面外）座標は画面左上を原点(0, 0)とする。右方向に行くほどxの正の値。下方向に行くほどyの正の値。
state = "idle"  # coming / blocked / idle

# 払い判定のための前フレームの手の位置
prev_hand_x = None

with mp_face.FaceDetection(
    model_selection=0, min_detection_confidence=0.7
) as face_detection, mp_hands.Hands(
    max_num_hands=2, min_detection_confidence=0.7
) as hands:

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        h, w, _ = frame.shape
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # 顔認識
        face_result = face_detection.process(rgb)
        face_center = None
        if face_result.detections:
            det = face_result.detections[0]
            box = det.location_data.relative_bounding_box
            cx = int((box.xmin + box.width / 2) * w)
            cy = int((box.ymin + box.height / 2) * h)
            face_center = (cx, cy)  # 顔の中心座標

        # 手認識
        hands_result = hands.process(rgb)
        swipe_detected = False

        if hands_result.multi_hand_landmarks:
            for hand_landmarks in hands_result.multi_hand_landmarks:
                # index finger tip (8番)：人差し指のこと
                # 人差し指のx, y座標を取得している
                x = int(hand_landmarks.landmark[8].x * w)
                y = int(hand_landmarks.landmark[8].y * h)

                # 払い判定：前フレームから横移動が大きい
                # absはabsolute value絶対値のこと
                if prev_hand_x is not None and abs(x - prev_hand_x) > 40:
                    swipe_detected = True

                # 「前の位置」を更新
                # 今回の判定では横方向しか見ていないのでprev_hand_yがない（左右に手を払いのけるため）
                prev_hand_x = x

        # 状態遷移
        if face_center:
            if state == "idle":
                # 顔が映ったら広告を接近開始
                ad_x, ad_y = -200, face_center[1]
                state = "coming"

            if state == "coming":
                # 顔の中心に近づく
                # face_center = (cx, cy) で取得した顔面中心のx座標、y座標をインデックスにしている
                # 顔の中心(cx, cy)めがけて移動する
                ad_x += (face_center[0] - ad_x) * 0.1  # cx - ad_x → 広告と顔の中心の距離（px）| 0.1：その距離の10パーセントだけ動く
                ad_y += (face_center[1] - ad_y) * 0.1  # cy - ad_y

                if swipe_detected:
                    state = "blocked"

            if state == "blocked":
                # 手で払われたので外側へ逃げる
                ad_x -= 50
                if ad_x < -200:
                    state = "idle"

        else:
            # 顔が映ってないときは広告非表示
            state = "idle"

        # 広告を描画
        # cv2.rectangle(画像, 左上座標, 右下座標, 色(BGR), 線の太さ)
        if state in ("coming", "blocked"):
            cv2.rectangle(
                frame,
                (int(ad_x) - 50, int(ad_y) - 30),
                (int(ad_x) + 50, int(ad_y) + 30),
                (0, 0, 255),
                2,
            )

        cv2.imshow("Ad Demo", frame)
        if cv2.waitKey(1) & 0xFF == 27:
            break

cap.release()
cv2.destroyAllWindows()
