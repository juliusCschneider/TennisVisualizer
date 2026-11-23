import json
import os
import cv2
import numpy as np
from ultralytics import YOLO

# COCO 17 keypoint names & skeleton connections
KP_NAMES = [
    "nose", "left_eye", "right_eye", "left_ear", "right_ear",
    "left_shoulder", "right_shoulder", "left_elbow", "right_elbow",
    "left_wrist", "right_wrist", "left_hip", "right_hip",
    "left_knee", "right_knee", "left_ankle", "right_ankle",
]

SKELETON_EDGES = [
    (5, 6), (5, 11), (6, 12), (11, 12),        # Torso
    (5, 7), (7, 9), (6, 8), (8, 10),           # Arms
    (11, 13), (13, 15), (12, 14), (14, 16),    # Legs
]


def filter_and_interpolate_ball(
    raw_candidates_per_frame,
    frame_width,
    max_speed_px_per_frame=95.0,
    min_cluster_neighbors=2,
    max_interp_gap=10,
):
    """
    Filters out stray false-positive jumps across the frame and interpolates short gaps:
      1. Keeps only detections that have temporal neighbors nearby (eliminates isolated jumps).
      2. Selects the candidate closest to the expected trajectory within a velocity gate.
      3. Interpolates missing/filtered gaps up to `max_interp_gap` frames.
    """
    num_frames = len(raw_candidates_per_frame)
    max_speed = max(max_speed_px_per_frame, frame_width * 0.08)

    # --- Step 1: Temporal Neighborhood Support (rejects 1-5 frame teleports across screen) ---
    supported_candidates = [[] for _ in range(num_frames)]
    window = 4  # Look +/- 4 frames around current frame

    for i in range(num_frames):
        for cand in raw_candidates_per_frame[i]:
            cx, cy = cand["center"]
            neighbor_hits = 0
            for j in range(max(0, i - window), min(num_frames, i + window + 1)):
                if i == j:
                    continue
                dt = abs(i - j)
                for other in raw_candidates_per_frame[j]:
                    ox, oy = other["center"]
                    dist = np.hypot(cx - ox, cy - oy)
                    if dist <= max_speed * dt:
                        neighbor_hits += 1
                        break  # Count at most 1 supporting match per neighboring frame

            if neighbor_hits >= min_cluster_neighbors:
                supported_candidates[i].append(cand)

    # --- Step 2: Sequential Kinematic Gating (pick candidate matching current velocity) ---
    filtered = [None] * num_frames
    last_idx = None
    last_pos = None
    velocity = np.array([0.0, 0.0])

    for i in range(num_frames):
        cands = supported_candidates[i]
        if not cands:
            continue

        if last_pos is None:
            # First valid anchor: pick highest-confidence supported detection
            best = max(cands, key=lambda c: c["conf"])
            filtered[i] = {
                "center": best["center"],
                "conf": best["conf"],
                "label": best["label"],
                "interpolated": False,
            }
            last_idx = i
            last_pos = np.array(best["center"], dtype=float)
        else:
            dt = i - last_idx
            # If the gap was huge (e.g., ball left screen and a new ball appeared much later), reset anchor
            if dt > max_interp_gap * 2:
                best = max(cands, key=lambda c: c["conf"])
                filtered[i] = {
                    "center": best["center"],
                    "conf": best["conf"],
                    "label": best["label"],
                    "interpolated": False,
                }
                last_idx = i
                last_pos = np.array(best["center"], dtype=float)
                velocity = np.array([0.0, 0.0])
                continue

            pred_pos = last_pos + velocity * dt
            valid_matches = []
            for c in cands:
                pos = np.array(c["center"], dtype=float)
                dist_from_last = np.linalg.norm(pos - last_pos)
                dist_from_pred = np.linalg.norm(pos - pred_pos)

                # Gate: cannot move faster than max_speed * dt
                if dist_from_last <= max_speed * dt:
                    # Score combines proximity to predicted path + detector confidence
                    score = dist_from_pred - 25.0 * c["conf"]
                    valid_matches.append((score, c, pos))

            if valid_matches:
                valid_matches.sort(key=lambda x: x[0])
                _, best, best_pos = valid_matches[0]
                filtered[i] = {
                    "center": best["center"],
                    "conf": best["conf"],
                    "label": best["label"],
                    "interpolated": False,
                }
                # Exponential smoothing on velocity estimate
                inst_vel = (best_pos - last_pos) / dt
                velocity = 0.6 * inst_vel + 0.4 * velocity
                last_idx = i
                last_pos = best_pos

    # --- Step 3: Interpolate Gaps Between Valid Anchors ---
    valid_indices = [i for i, item in enumerate(filtered) if item is not None]
    for k in range(len(valid_indices) - 1):
        idx_a = valid_indices[k]
        idx_b = valid_indices[k + 1]
        gap = idx_b - idx_a

        if 1 < gap <= max_interp_gap:
            p_a = np.array(filtered[idx_a]["center"], dtype=float)
            p_b = np.array(filtered[idx_b]["center"], dtype=float)

            for step in range(1, gap):
                alpha = step / float(gap)
                interp_pt = (1.0 - alpha) * p_a + alpha * p_b
                filtered[idx_a + step] = {
                    "center": [round(float(interp_pt[0]), 2), round(float(interp_pt[1]), 2)],
                    "conf": 0.0,
                    "label": "interpolated",
                    "interpolated": True,
                }

    return filtered


def run_combined_tracker(
    video_path="Videos/tennis4.mp4",
    output_dir="/Users/christophmissall/Desktop/Tennis_334/TennisVisualizer/results",
    show_window=True,
):
    os.makedirs(output_dir, exist_ok=True)

    pose_model = YOLO("yolo26m-pose.pt")
    ball_model = YOLO("training/yolo11s.pt")

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise FileNotFoundError(f"Could not open video: {video_path}")

    fps = float(cap.get(cv2.CAP_PROP_FPS) or 60.0)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    video_name = os.path.splitext(os.path.basename(video_path))[0]
    out_video_path = os.path.join(output_dir, f"{video_name}_tracked.mp4")
    out_json_path = os.path.join(output_dir, f"{video_name}_tracking.json")

    raw_frames = []
    player_kps_list = []
    raw_ball_candidates = []

    print(f"Pass 1/2: Running pose & ball detection on '{video_path}'...")
    frame_id = 0
    while True:
        ret, frame = cap.read()
        print(f"{frame_id} at {fps} frames ")
        frame_id+=1
        if not ret:
            break

        # 1. Detect Player Pose
        pose_res = pose_model.predict(frame, conf=0.35, device="mps", verbose=False)[0]
        player_kps = None
        if pose_res.keypoints is not None and len(pose_res.keypoints.xy) > 0:
            kps = pose_res.keypoints.xy[0].cpu().numpy()
            player_kps = {
                KP_NAMES[i]: [round(float(kps[i][0]), 2), round(float(kps[i][1]), 2)]
                for i in range(len(KP_NAMES))
            }

        # 2. Collect ALL candidate ball detections (instead of only top-1)
        ball_res = ball_model.predict(
            frame,
            classes=[29, 32],  # 29 = frisbee, 32 = sports ball
            conf=0.20,
            imgsz=1280,
            device="mps",
            verbose=False,
        )[0]

        frame_cands = []
        if len(ball_res.boxes) > 0:
            for b_idx in range(len(ball_res.boxes)):
                box = ball_res.boxes.xyxy[b_idx].cpu().numpy()
                conf = float(ball_res.boxes.conf[b_idx])
                cls_id = int(ball_res.boxes.cls[b_idx])
                cx = round(float(0.5 * (box[0] + box[2])), 2)
                cy = round(float(0.5 * (box[1] + box[3])), 2)
                frame_cands.append({
                    "center": [cx, cy],
                    "bbox": [round(float(v), 1) for v in box],
                    "conf": round(conf, 3),
                    "label": ball_model.names[cls_id],
                })

        raw_frames.append(frame)
        player_kps_list.append(player_kps)
        raw_ball_candidates.append(frame_cands)

    cap.release()

    # --- Pass 2: Filter outliers & interpolate missing gaps ---
    print("Pass 2/2: Filtering false-positive jumps & interpolating trajectory gaps...")
    clean_balls = filter_and_interpolate_ball(
        raw_ball_candidates,
        frame_width=width,
        max_speed_px_per_frame=95.0,  # Tune higher (e.g., 130) if serve smash moves >95 px/frame
        min_cluster_neighbors=2,      # Requires agreement across at least 2 nearby frames
        max_interp_gap=10,            # Interpolates across gaps up to 10 frames
    )

    writer = cv2.VideoWriter(
        out_video_path, cv2.VideoWriter_fourcc(*"mp4v"), fps, (width, height)
    )

    frames_log = []
    ball_trail = []

    for frame_idx, frame in enumerate(raw_frames):
        print(frame_idx)
        vis = frame.copy()
        player_kps = player_kps_list[frame_idx]
        ball_info = clean_balls[frame_idx]

        # Draw Player Skeleton
        if player_kps is not None:
            pts = list(player_kps.values())
            for i, j in SKELETON_EDGES:
                if pts[i][0] > 0 and pts[j][0] > 0:
                    cv2.line(
                        vis,
                        (int(pts[i][0]), int(pts[i][1])),
                        (int(pts[j][0]), int(pts[j][1])),
                        (255, 200, 0), 2, cv2.LINE_AA
                    )
            for pt in pts:
                if pt[0] > 0:
                    cv2.circle(vis, (int(pt[0]), int(pt[1])), 4, (0, 255, 128), -1)

        # Draw Filtered / Interpolated Ball
        if ball_info is not None:
            cx, cy = int(ball_info["center"][0]), int(ball_info["center"][1])
            if ball_info["interpolated"]:
                # Orange circle for interpolated frames
                cv2.circle(vis, (cx, cy), 7, (0, 165, 255), 2, cv2.LINE_AA)
                cv2.putText(
                    vis, "interp", (cx + 10, cy - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 165, 255), 1, cv2.LINE_AA
                )
            else:
                # Yellow circle + red center for verified detections
                cv2.circle(vis, (cx, cy), 8, (0, 255, 255), 2, cv2.LINE_AA)
                cv2.circle(vis, (cx, cy), 3, (0, 0, 255), -1)
                cv2.putText(
                    vis, f"{ball_info['label']} {ball_info['conf']:.2f}",
                    (cx + 10, cy - 6),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 2, cv2.LINE_AA
                )

        ball_trail.append(ball_info["center"] if ball_info else None)

        # Draw Continuous Ball Trajectory Trail
        for k in range(1, len(ball_trail)):
            if ball_trail[k - 1] is not None and ball_trail[k] is not None:
                p1 = (int(ball_trail[k - 1][0]), int(ball_trail[k - 1][1]))
                p2 = (int(ball_trail[k][0]), int(ball_trail[k][1]))
                cv2.line(vis, p1, p2, (0, 255, 255), 2, cv2.LINE_AA)

        frames_log.append({
            "frame": frame_idx,
            "time": round(frame_idx / fps, 4),
            "player_keypoints_2d": player_kps,
            "ball_2d": ball_info,
        })

        writer.write(vis)
        if show_window:
            cv2.imshow("Filtered Player & Ball Tracking (Press 'q' to quit)", vis)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                show_window = False

    writer.release()
    cv2.destroyAllWindows()

    with open(out_json_path, "w") as f:
        json.dump({"video": video_path, "fps": fps, "frames": frames_log}, f, indent=2)

    print(f"[OK] Saved filtered video -> {out_video_path}")
    print(f"[OK] Saved clean 2D tracking JSON -> {out_json_path}")


if __name__ == "__main__":
    run_combined_tracker("Videos/tennis4.mp4")
