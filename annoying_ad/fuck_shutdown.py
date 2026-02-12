"""
ジェスチャー検知モジュール
中指を立てるポーズを検知する機能を提供
"""

import cv2


def check_middle_finger_gesture(hand_landmarks, w, h):
    """
    中指を立てているかどうかを判定する関数

    Args:
        hand_landmarks: MediaPipeの手のランドマーク
        w: 画像の幅
        h: 画像の高さ

    Returns:
        bool: 中指が立っている場合True、そうでない場合False
    """
    # ランドマークの座標を取得
    landmarks = hand_landmarks.landmark

    # # 中指の先端（12）と付け根（9）のy座標を比較
    # middle_tip_y = landmarks[12].y * h
    # middle_base_y = landmarks[9].y * h

    # # 中指が上を向いているか（先端が付け根より上）
    # middle_finger_up = middle_tip_y < middle_base_y

    # # 他の指が曲がっているかチェック
    # # 親指（4と3）
    # thumb_tip_y = landmarks[4].y * h
    # thumb_joint_y = landmarks[3].y * h
    # thumb_down = thumb_tip_y > thumb_joint_y

    # # 人差し指（8と6）
    # index_tip_y = landmarks[8].y * h
    # index_joint_y = landmarks[6].y * h
    # index_down = index_tip_y > index_joint_y

    # # 薬指（16と13）
    # ring_tip_y = landmarks[16].y * h
    # ring_joint_y = landmarks[13].y * h
    # ring_down = ring_tip_y > ring_joint_y

    # # 小指（20と17）
    # pinky_tip_y = landmarks[20].y * h
    # pinky_joint_y = landmarks[17].y * h
    # pinky_down = pinky_tip_y > pinky_joint_y

    """
    中指以外の指先が、中指第二関節(pip)と中指つけね(base) の間に存在するときを「fuck」の状態としている
    middle_pip < 他の指先 < middle_base
    """
    # 中指　ここだけまっすぐ立つ
    middle_tip_y = landmarks[12].y * h
    middle_base_y = landmarks[9].y * h
    middle_pip_y = landmarks[10].y * h  # 第二関節
    middle_finger_up = middle_tip_y < middle_base_y

    # 親指
    thumb_tip_y = landmarks[4].y * h
    thumb_down = middle_pip_y < thumb_tip_y < middle_base_y

    # 人差し指
    index_tip_y = landmarks[8].y * h
    index_down = middle_pip_y < index_tip_y < middle_base_y

    # 薬指
    ring_tip_y = landmarks[16].y * h
    ring_down = middle_pip_y < ring_tip_y < middle_base_y

    # 小指
    pinky_tip_y = landmarks[20].y * h
    pinky_down = middle_pip_y < pinky_tip_y < middle_base_y

    # 中指が立っていて、他の指が曲がっている場合
    if middle_finger_up and thumb_down and index_down and ring_down and pinky_down:
        return True

    return False


def draw_hand_landmarks(frame, hand_landmarks, w, h):
    """
    手のランドマークを画面に描画するデバッグ関数

    Args:
        frame: OpenCVのフレーム
        hand_landmarks: 手のランドマーク
        w: 画像の幅
        h: 画像の高さ
    """
    landmarks = hand_landmarks.landmark

    # 重要なポイントを描画
    important_points = [
        (4, "oy", (0, 255, 0)),  # 緑
        (8, "ht", (255, 0, 0)),  # 青
        (12, "nk", (0, 0, 255)),  # 赤
        (16, "ks", (255, 255, 0)),  # シアン
        (20, "ky", (255, 0, 255)),  # マゼンタ
        (9, "nkTukene", (128, 128, 128)),  # グレー
    ]

    for idx, name, color in important_points:
        x = int(landmarks[idx].x * w)
        y = int(landmarks[idx].y * h)
        cv2.circle(frame, (x, y), 10, color, -1)  # 円を描画
        cv2.putText(frame, name, (x + 15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # 中指の状態を線で表示
    middle_tip_x = int(landmarks[12].x * w)
    middle_tip_y = int(landmarks[12].y * h)
    middle_base_x = int(landmarks[9].x * w)
    middle_base_y = int(landmarks[9].y * h)
    cv2.line(
        frame,
        (middle_base_x, middle_base_y),
        (middle_tip_x, middle_tip_y),
        (0, 0, 255),
        2,
    )


def is_fuck(hands_result, w, h):
    """
    手の検出結果から中指を立てているかどうかをチェックする

    Args:
        hands_result: MediaPipeの手検出結果
        w: 画像の幅
        h: 画像の高さ

    Returns:
        bool: 中指が検出された場合True、そうでない場合False
    """
    if not hands_result.multi_hand_landmarks:
        return False

    # 検出されたすべての手をチェック　複数の手検出対応
    for hand_landmarks in hands_result.multi_hand_landmarks:
        if check_middle_finger_gesture(hand_landmarks, w, h):
            return True

    return False
