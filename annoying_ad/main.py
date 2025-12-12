import cv2
import mediapipe as mp
import time

from ad_object import AdObject, random_start

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

            else:
                hand_debug_msg = "no hand detected"

            # 顔が見えている時だけ広告オブジェクトを出現させる
            if face_center:
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
            instruct_msg1 = "If advertisement appears, "
            instruct_msg2 = "shake your hand to dismiss it"
            cv2.putText(frame, instruct_msg1, (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
            cv2.putText(frame, instruct_msg2, (10, 60),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

            cv2.imshow(window_name, frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESCで終了
                break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
