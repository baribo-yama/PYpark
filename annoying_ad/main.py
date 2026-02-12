from pydoc import describe
import cv2
import mediapipe as mp
import time
from pathlib import Path

from ad_object import AdObject, random_start
from fuck_shutdown import check_middle_finger_gesture, is_fuck, draw_hand_landmarks

# 広告表示のオンオフを切り替えるデバッグフラグ
enable_ads = True  # Trueで表示、Falseで非表示

# fuckdownのオンオフ切り替え
enable_fuckdown = False

# Mediapipenの初期化
mp_face = mp.solutions.face_detection
mp_hands = mp.solutions.hands


def main():
    cap = cv2.VideoCapture(0)

    # 管理する広告オブジェクトリスト
    ads = []

    # 払い動作の判定用
    prev_hand_x = None

    # 広告生成のタイミング制御
    last_spawn = time.time()

    # model_selection=0 は近距離の顔を検知するモデル。1は遠距離の人混みなどでの検知用
    with mp_face.FaceDetection(
        model_selection=0, min_detection_confidence=0.7
    ) as face_det, mp_hands.Hands(
        max_num_hands=2, min_detection_confidence=0.7
    ) as hands:

        # ウィンドウを作成（リサイズ可能にする）
        window_name = "Ad System MVP"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)

        # アプリ起動時にウィンドウを最前面に
        # 引数の1は、topmostを有効にする、という意味らしい
        cv2.setWindowProperty(window_name, cv2.WND_PROP_TOPMOST, 1)

        # ウィンドウサイズを指定
        cv2.resizeWindow(window_name, 1280, 720)

        f"if advertisement appear, shake your hand from left to right"


        while True:
            ret, frame = cap.read()
            if not ret:
                break

            h, w, _ = frame.shape
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # 顔検出
            face_res = face_det.process(rgb)
            face_center = None

            if face_res.detections:
                det = face_res.detections[0]
                box = det.location_data.relative_bounding_box
                cx = int((box.xmin + box.width / 2) * w)
                cy = int((box.ymin + box.height / 2) * h)
                face_center = (cx, cy)

            # 払い動作（手の方向スワイプ）を検知
            hands_res = hands.process(rgb)
            swipe_detected = False
            hand_debug_msg = ""  # 画面表示デバッグメッセージ用

            if hands_res.multi_hand_landmarks:
                hand_count = len(hands_res.multi_hand_landmarks)
                hand_debug_msg = f"hand detected (count: {hand_count})"

                # enumerateでインデックスを表示させる（iがインデックスを担当）
                for i, hand in enumerate(hands_res.multi_hand_landmarks):
                    x = int(hand.landmark[8].x * w)  # 人差し指先のx座標

                    # 人差し指の座標も表示
                    hand_debug_msg += f" | hand{i+1}: x={x}"

                    # ～以上動いたらスワイプ
                    if prev_hand_x is not None and abs(x - prev_hand_x) > 100:
                        swipe_detected = True
                        hand_debug_msg += "[swipe detected!]"

                    prev_hand_x = x

                    # デバッグ: ランドマークを描画 fuckデバッグ用
                    # draw_hand_landmarks(frame, hand, w, h)

            else:
                hand_debug_msg = "no hand detected"

            # 顔が見えている時だけ広告オブジェクトを出現させる
            if enable_ads and face_center:
                if time.time() - last_spawn > 1.5:  # 1.5秒ごとに広告生成
                    start_pos = random_start(w, h)
                    ads.append(AdObject(start_pos))
                    last_spawn = time.time()

            # 広告の更新処理
            for ad in ads:
                if face_center:
                    ad.update(face_center, swipe_detected)

            # 消すべき広告（state == "remove"）を排除
            ads = [ad for ad in ads if ad.state != "remove"]

            # 描画
            for ad in ads:
                ad.draw(frame)

            # デバッグ情報を画面に表示
            # cv2.putText(frame, hand_debug_msg, (10, 30),
            # cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,255, 0), 2)

            # システムの説明
            # instruct_msg1 = "If advertisement appears, "  # (10, 30)
            # instruct_msg2 = "shake your hand to dismiss it"
            # cv2.putText(frame, instruct_msg1, (10, 30),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
            # cv2.putText(frame, instruct_msg2, (10, 60),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

            # システム説明画像
            img_path = Path(__file__).parent / "img" / "ad_describe.png"
            describe_img = cv2.imread(str(img_path))
            describe_img = cv2.resize(describe_img, (200, 75))

            ih, iw = describe_img.shape[:2]
            frame[0:ih, 0:iw] = describe_img

            # 画面への出力
            cv2.imshow(window_name, frame)

            if cv2.waitKey(1) & 0xFF == 27:  # ESCで終了
                print("escが押された")
                break

            if enable_fuckdown == True:
                if is_fuck(hands_res, w, h):
                    print("fuck detected!!")
                    shutdownText = "...fuck_you"

                    # テキストのサイズを取得
                    font = cv2.FONT_HERSHEY_TRIPLEX
                    font_scale = 1.0 # フォントの大きさ
                    font_color = (0, 0, 255) # フォント：赤
                    thickness = 2 # フォントの太さ

                    (text_width, text_height), baseline = cv2.getTextSize(
                        shutdownText, font, font_scale, thickness
                    )

                    # 画面の中心座標を計算（テキストの中心が画面の中心になるように）
                    text_x = (w - text_width) // 2
                    text_y = (h + text_height) // 2 # putTextは左下角を指定するため

                    cv2.putText(frame, shutdownText, (text_x, text_y),
                                font, font_scale, font_color, thickness)
                    cv2.imshow(window_name, frame)
                    cv2.waitKey(2000)
                    break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
