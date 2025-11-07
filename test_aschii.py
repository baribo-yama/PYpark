import cv2
import numpy as np
import mediapipe as mp

# 文字パレット（""内の文字は左の文字ほど濃い、右の文字ほど薄いものとして設定される）
ASCII_CHARS = "@%#*+=-:"  # デフォルト @%#*+=-:.
# 文字サイズ・グリッド設定
CELL_W, CELL_H = 8, 12         # 1文字を描くピクセル幅/高さ
FONT = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.4
THICKNESS = 1

mp_hands = mp.solutions.hands
mp_face = mp.solutions.face_detection
mp_drawing = mp.solutions.drawing_utils

def landmarks_to_mask(img_shape, landmarks, image_w, image_h):
    # ランドマークを画素座標へ
    pts = []
    for lm in landmarks:
        x = int(lm.x * image_w)
        y = int(lm.y * image_h)
        pts.append([x, y])
    pts = np.array(pts, dtype=np.int32)
    # 凸包で手領域を近似（指の隙間も埋める）
    hull = cv2.convexHull(pts)
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    cv2.fillConvexPoly(mask, hull, 255)
    return mask

def density_to_char(density):
    # 0.0~1.0 を文字パレットへ
    idx = int((1.0 - density) * (len(ASCII_CHARS) - 1))
    return ASCII_CHARS[max(0, min(idx, len(ASCII_CHARS)-1))]

def face_to_mask(img_shape, detection, image_w, image_h):
    """顔のバウンディングボックスからマスクを作成"""
    bbox = detection.location_data.relative_bounding_box

    # 相対座標をピクセル座標に変換
    x = int(bbox.xmin * image_w)
    y = int(bbox.ymin * image_h)
    w = int(bbox.width * image_w)
    h = int(bbox.height * image_h)

    # マスク作成
    mask = np.zeros(img_shape[:2], dtype=np.uint8)
    cv2.rectangle(mask, (x, y), (x + w, y + h), 255, -1)  # -1で塗りつぶし
    return mask

# ウィンドウサイズ設定
WIDTH, HEIGHT = 960, 540  # デフォルトは640, 360 ← 解像度を小さめにして軽くする

cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, WIDTH)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HEIGHT)

face_detector = mp_face.FaceDetection(model_selection=0, min_detection_confidence=0.5)

with mp_hands.Hands(
    max_num_hands=2,
    model_complexity=0,
    min_detection_confidence=0.6,
    min_tracking_confidence=0.5
) as hands:

    while True:
        ok, frame = cap.read()
        if not ok:
            break

        # 処理用に左右反転（鏡映りっぽく）
        frame = cv2.flip(frame, 1)
        h, w = frame.shape[:2]

        # MediaPipeはRGBを想定
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = hands.process(rgb)
        face_result = face_detector.process(rgb)

        ascii_canvas = np.zeros((h, w, 3), dtype=np.uint8)  # 黒背景

        # グレースケール変換（手と顔の処理で共通使用）
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if result.multi_hand_landmarks:
            # 両手に対して処理
            for hand_landmarks in result.multi_hand_landmarks:

                # 手マスク（白=手）
                mask = landmarks_to_mask(frame.shape, hand_landmarks.landmark, w, h)

                # グリッドを回して手マスク内だけ文字化
                for y in range(0, h, CELL_H):
                    for x in range(0, w, CELL_W):
                        y2 = min(y + CELL_H, h)
                        x2 = min(x + CELL_W, w)

                        cell_mask = mask[y:y2, x:x2]
                        if cell_mask.size == 0:
                            continue

                        # 手領域の占有率（density）を計算
                        fill = np.count_nonzero(cell_mask) / cell_mask.size
                        if fill < 0.1:
                            # 手がほとんど無いセルはスキップ（ノイズ除去）
                            continue

                        # 手領域の平均明るさ（手領域に限定）
                        cell_gray = gray[y:y2, x:x2]
                        mean_on_hand = cv2.mean(cell_gray, mask=cell_mask)[0]  # 0~255

                        # 明るさ→密度に反転（暗い=濃い文字）
                        density = 1.0 - (mean_on_hand / 255.0)
                        ch = density_to_char(density)

                        # セル中央に文字描画
                        text_size, _ = cv2.getTextSize(ch, FONT, FONT_SCALE, THICKNESS)
                        tx = x + (CELL_W - text_size[0]) // 2
                        ty = y + (CELL_H + text_size[1]) // 2
                        cv2.putText(ascii_canvas, ch, (tx, ty), FONT, FONT_SCALE, (255, 255, 255), THICKNESS, cv2.LINE_AA)

        if face_result.detections:
            # 検出されたすべての顔に対して処理
            for detection in face_result.detections:

                # 顔マスク（白=顔）
                face_mask = face_to_mask(frame.shape, detection, w, h)

                # グリッドを回して顔マスク内だけ文字化
                for y in range(0, h, CELL_H):
                    for x in range(0, w, CELL_W):
                        y2 = min(y + CELL_H, h)
                        x2 = min(x + CELL_W, w)

                        cell_mask = face_mask[y:y2, x:x2]
                        if cell_mask.size == 0:
                            continue

                        # 顔領域の占有率を計算
                        fill = np.count_nonzero(cell_mask) / cell_mask.size
                        if fill < 0.1:
                            # 顔がほとんどないセルはスキップ
                            continue

                        # 顔領域の平均明るさ
                        cell_gray = gray[y:y2, x:x2]
                        mean_on_face = cv2.mean(cell_gray, mask=cell_mask)[0]

                        # 明るさ→密度に反転（暗い＝濃い文字）
                        density = 1.0 - (mean_on_face / 255.0)
                        ch = density_to_char(density)

                        # セル中央に文字描画
                        text_size, _ = cv2.getTextSize(ch, FONT, FONT_SCALE, THICKNESS)
                        tx = x + (CELL_W - text_size[0]) // 2
                        ty = y + (CELL_H + text_size[1]) // 2
                        cv2.putText(ascii_canvas, ch, (tx, ty), FONT, FONT_SCALE, (255, 255, 255), THICKNESS, cv2.LINE_AA)

        # 表示
        cv2.imshow("ASCII Hand", ascii_canvas)

        # qキーを押して終了
        key = cv2.waitKey(1) & 0xFF
        if key == 27 or key == ord('q'):
            break

cap.release()
face_detector.close()
cv2.destroyAllWindows()
