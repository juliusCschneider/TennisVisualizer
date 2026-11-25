import json
import math
import os
import cv2
import numpy as np

# standard Tennis Court Dimensions (in meters)
# origin (0, 0, 0) is the center of the net on the court floor (Y = 0)
# +Z is the near half (server side, baseline at +11.885m)
# -Z is the far half (receiver side, baseline at -11.885m)
SINGLES_HALF_W = 4.115     # 8.23m total singles width
DOUBLES_HALF_W = 5.485     # 10.97m total doubles width
SERVICE_LINE_Z = 6.40      # 6.40m from net to service line
BASELINE_Z = 11.885        # 11.885m from net to baseline
NET_HEIGHT_CENTER = 0.914  # 0.914m (3 ft) at center
NET_HEIGHT_POST = 1.07     # 1.07m (3.5 ft) at doubles posts

#all of the above data was provided by Gemini

CALIB_POINTS_SPEC = [
    ("1: Near Baseline + Left Singles Line",    [-SINGLES_HALF_W,  BASELINE_Z]),
    ("2: Near Baseline + Right Singles Line",   [ SINGLES_HALF_W,  BASELINE_Z]),
    ("3: Net Ground Line + Left Singles Line",  [-SINGLES_HALF_W,  0.0]),
    ("4: Net Ground Line + Right Singles Line", [ SINGLES_HALF_W,  0.0]),
    ("5: Far Service Line + Left Singles Line", [-SINGLES_HALF_W, -SERVICE_LINE_Z]),
    ("6: Far Service Line + Right Singles Line",[ SINGLES_HALF_W, -SERVICE_LINE_Z]),
    ("7: Far Baseline + Left Singles Line",     [-SINGLES_HALF_W, -BASELINE_Z]),
    ("8: Far Baseline + Right Singles Line",    [ SINGLES_HALF_W, -BASELINE_Z]),
]

CALIB_COURT_PTS_M = np.array([pt for _, pt in CALIB_POINTS_SPEC], dtype=np.float32)

# All ground court lines in (X, Z) meters for OpenGL & 2D video projection
COURT_LINES_M = [
    # Near & Far Baselines (Doubles width)
    [(-DOUBLES_HALF_W,  BASELINE_Z), ( DOUBLES_HALF_W,  BASELINE_Z)],
    [(-DOUBLES_HALF_W, -BASELINE_Z), ( DOUBLES_HALF_W, -BASELINE_Z)],
    # Doubles Sidelines
    [(-DOUBLES_HALF_W, -BASELINE_Z), (-DOUBLES_HALF_W,  BASELINE_Z)],
    [( DOUBLES_HALF_W, -BASELINE_Z), ( DOUBLES_HALF_W,  BASELINE_Z)],
    # Singles Sidelines
    [(-SINGLES_HALF_W, -BASELINE_Z), (-SINGLES_HALF_W,  BASELINE_Z)],
    [( SINGLES_HALF_W, -BASELINE_Z), ( SINGLES_HALF_W,  BASELINE_Z)],
    # Near & Far Service Lines
    [(-SINGLES_HALF_W,  SERVICE_LINE_Z), ( SINGLES_HALF_W,  SERVICE_LINE_Z)],
    [(-SINGLES_HALF_W, -SERVICE_LINE_Z), ( SINGLES_HALF_W, -SERVICE_LINE_Z)],
    # Center Service Line & Baseline Center Marks
    [(0.0, -SERVICE_LINE_Z), (0.0, SERVICE_LINE_Z)],
    [(0.0,  BASELINE_Z - 0.15), (0.0,  BASELINE_Z)],
    [(0.0, -BASELINE_Z + 0.15), (0.0, -BASELINE_Z)],
    # Net Ground Line (Z = 0)
    [(-DOUBLES_HALF_W, 0.0), (DOUBLES_HALF_W, 0.0)],
]

# Skeleton bone pairs for OpenGL rendering
BONES = [
    ("left_shoulder", "right_shoulder"),
    ("left_shoulder", "left_hip"), ("right_shoulder", "right_hip"),
    ("left_hip", "right_hip"),
    ("left_shoulder", "left_elbow"), ("left_elbow", "left_wrist"),
    ("right_shoulder", "right_elbow"), ("right_elbow", "right_wrist"),
    ("left_hip", "left_knee"), ("left_knee", "left_ankle"),
    ("right_hip", "right_knee"), ("right_knee", "right_ankle"),
    ("neck", "head_center"),
]

# Anatomical bone lengths (meters) for 2D -> 3D Z-depth foreshortening
BONE_LENGTHS_M = {
    ("left_shoulder", "left_elbow"): 0.30, ("left_elbow", "left_wrist"): 0.26,
    ("right_shoulder", "right_elbow"): 0.30, ("right_elbow", "right_wrist"): 0.26,
    ("left_hip", "left_knee"): 0.43, ("left_knee", "left_ankle"): 0.42,
    ("right_hip", "right_knee"): 0.43, ("right_knee", "right_ankle"): 0.42,
}


def click_court_keypoints(frame):
    """Interactive 8-point full-court calibration on frame 0."""
    clicked = []
    total_pts = len(CALIB_POINTS_SPEC)

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN and len(clicked) < total_pts:
            clicked.append([float(x), float(y)])

    win_name = "Full-Court Calibration (Click 8 Points | 'u'=Undo, 'r'=Reset, 'Enter'=Confirm)"
    cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    cv2.setMouseCallback(win_name, on_mouse)

    while True:
        disp = frame.copy()
        if len(clicked) < total_pts:
            prompt = f"Click Point {CALIB_POINTS_SPEC[len(clicked)][0]}  ({len(clicked)}/{total_pts})"
            banner_color = (0, 255, 255)
        else:
            prompt = "All 8 points set! Press ENTER to continue (or 'u' to undo)"
            banner_color = (0, 255, 0)

        cv2.rectangle(disp, (10, 10), (760, 52), (20, 20, 20), -1)
        cv2.putText(disp, prompt, (20, 38), cv2.FONT_HERSHEY_SIMPLEX, 0.68, banner_color, 2)

        for idx, pt in enumerate(clicked):
            cx, cy = int(pt[0]), int(pt[1])
            cv2.circle(disp, (cx, cy), 6, (0, 0, 255), -1)
            cv2.putText(disp, str(idx + 1), (cx + 8, cy - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 0, 255), 2)
            if idx % 2 == 1:
                prev_pt = clicked[idx - 1]
                cv2.line(disp, (int(prev_pt[0]), int(prev_pt[1])), (cx, cy), (0, 255, 0), 2)

        cv2.imshow(win_name, disp)
        key = cv2.waitKey(20) & 0xFF
        if key == ord("u") and clicked:
            clicked.pop()
        elif key == ord("r"):
            clicked.clear()
        elif key in (13, 32) and len(clicked) == total_pts:
            break

    cv2.destroyWindow(win_name)
    return np.array(clicked, dtype=np.float32)


def draw_projected_court(frame, H_court_to_px):
    """Projects all 3D ITF court lines onto the video frame."""
    overlay = frame.copy()
    for (x1, z1), (x2, z2) in COURT_LINES_M:
        pts_m = np.array([[[x1, z1], [x2, z2]]], dtype=np.float32)
        pts_px = cv2.perspectiveTransform(pts_m, H_court_to_px)[0]
        p1 = (int(round(pts_px[0][0])), int(round(pts_px[0][1])))
        p2 = (int(round(pts_px[1][0])), int(round(pts_px[1][1])))

        if z1 == 0.0 and z2 == 0.0:
            color = (255, 255, 0)   # net ground line
        elif abs(z1) == BASELINE_Z and abs(z2) == BASELINE_Z:
            color = (0, 215, 255)   # baselines
        else:
            color = (0, 255, 0)     # sidelines and service Lines

        cv2.line(overlay, p1, p2, color, 2, cv2.LINE_AA)

    srv_px = cv2.perspectiveTransform(
        np.array([[[0.0, BASELINE_Z]]], dtype=np.float32), H_court_to_px
    )[0][0]
    cv2.circle(overlay, (int(round(srv_px[0])), int(round(srv_px[1]))), 7, (255, 0, 255), -1)
    return cv2.addWeighted(overlay, 0.78, frame, 0.22, 0)


def lift_player_to_court_3d(pts_2d, scale_m_per_px, anchor_3d=(0.0, 0.0, BASELINE_Z)):
    """
    Lifts 2D player pixel keypoints into 3D OpenGL court coordinates (meters, Y-up)
    and places the player's planted feet at `anchor_3d` = (0.0, 0.0, +11.885m).
    """
    if pts_2d is None:
        return None

    ax, ay, az = anchor_3d
    ankle_center_x = 0.5 * (pts_2d["left_ankle"][0] + pts_2d["right_ankle"][0])
    lowest_ankle_y = max(pts_2d["left_ankle"][1], pts_2d["right_ankle"][1])

    pts_3d = {}
    for name, (px, py) in pts_2d.items():
        if px <= 0 and py <= 0:
            pts_3d[name] = np.array([ax, ay, az], dtype=float)
            continue
        x_gl = ax + (px - ankle_center_x) * scale_m_per_px
        y_gl = ay + max(0.0, (lowest_ankle_y - py) * scale_m_per_px)
        pts_3d[name] = np.array([x_gl, y_gl, az], dtype=float)


    pts_3d["left_shoulder"][2] = az - 0.08
    pts_3d["right_shoulder"][2] = az + 0.08
    pts_3d["left_hip"][2] = az - 0.06
    pts_3d["right_hip"][2] = az + 0.06

    for (parent, child), target_len in BONE_LENGTHS_M.items():
        p_pos = pts_3d[parent]
        c_pos = pts_3d[child]
        dx = c_pos[0] - p_pos[0]
        dy = c_pos[1] - p_pos[1]
        dz = math.sqrt(max(0.0, target_len * target_len - (dx * dx + dy * dy)))


        sign = -1.0 if "wrist" in child or "elbow" in child else 1.0
        pts_3d[child][2] = p_pos[2] + sign * dz * 0.55

    pts_3d["neck"] = 0.5 * (pts_3d["left_shoulder"] + pts_3d["right_shoulder"])
    pts_3d["head_center"] = 0.5 * (pts_3d["left_ear"] + pts_3d["right_ear"])

    return {k: [round(float(c), 4) for c in v] for k, v in pts_3d.items()}

#TODO: The bounce identifies the point where the ball hits the racket as bounce. Needs fixing
def find_contact_and_bounce_frames(frames):
    """
    Finds:
      1. `contact_idx`: Highest ball point above server (racket strike apex, min pixel Y).
      2. `bounce_idx`: Sharp downward-to-upward reversal after contact (local max pixel Y).
    """
    ball_y = [(i, f["ball_2d"]["center"][1]) for i, f in enumerate(frames) if f["ball_2d"] is not None]
    if len(ball_y) < 6:
        return None, None

    contact_pos = int(np.argmin([y for _, y in ball_y]))
    contact_idx = ball_y[contact_pos][0]

    bounce_idx = None
    for k in range(contact_pos + 2, len(ball_y) - 2):
        _, y_prev = ball_y[k - 1]
        idx_curr, y_curr = ball_y[k]
        _, y_next = ball_y[k + 1]

        if y_curr >= y_prev and y_curr > y_next and (y_curr - y_next) > 3.0:
            bounce_idx = idx_curr
            break

    if bounce_idx is None:
        post_contact = ball_y[contact_pos + 1:]
        if post_contact:
            bounce_idx = max(post_contact, key=lambda item: item[1])[0]

    return contact_idx, bounce_idx


def reconstruct_3d_ball_arc(frames, fps, contact_idx, bounce_idx, bounce_3d):
    """
    Populates `ball_3d` = [X, Y, Z] in meters for every frame:
      - Pre-contact (toss): follows the ball's 2D vertical rise above the server baseline.
      - Contact -> Bounce: exact 3D projectile parabola connecting racket strike to `bounce_3d`.
      - Post-bounce: physical rebound trajectory using coefficient of restitution e = 0.72.
    """
    if contact_idx is None or bounce_idx is None or bounce_3d is None or bounce_idx <= contact_idx:
        return

    g = 9.81
    t0 = contact_idx / fps
    t1 = bounce_idx / fps
    dt_flight = max(0.05, t1 - t0)

    # Start point at racket contact: directly above server baseline [X0, Y0, +11.885m]
    contact_joints = frames[contact_idx].get("player_joints_3d")
    if contact_joints and "right_wrist" in contact_joints:
        rw = contact_joints["right_wrist"]
        p0 = np.array([rw[0], max(2.35, rw[1] + 0.45), BASELINE_Z - 0.35], dtype=float)
    else:
        p0 = np.array([0.0, 2.65, BASELINE_Z - 0.35], dtype=float)

    p1 = np.array(bounce_3d, dtype=float)  # [X_bounce, 0.0, Z_bounce]

    # Solve exact initial velocity (vx, vy0, vz) to hit p1 at t1 under gravity
    vx = (p1[0] - p0[0]) / dt_flight
    vz = (p1[2] - p0[2]) / dt_flight
    vy0 = (p1[1] - p0[1] + 0.5 * g * dt_flight * dt_flight) / dt_flight

    # Impact velocity just before bounce for post-bounce rebound
    vy_impact = vy0 - g * dt_flight
    vy_rebound = -0.72 * vy_impact

    # Find first valid ball detection for toss start
    toss_indices = [
        i for i in range(0, contact_idx + 1)
        if frames[i]["ball_2d"] is not None
    ]
    toss_start_idx = toss_indices[0] if toss_indices else max(0, contact_idx - 15)

    for i, f in enumerate(frames):
        t = i / fps
        if toss_start_idx <= i < contact_idx:
            # Smooth toss rise from left_wrist to contact point p0
            alpha = (i - toss_start_idx) / max(1.0, float(contact_idx - toss_start_idx))
            joints = f.get("player_joints_3d")
            if joints and "left_wrist" in joints:
                lw = np.array(joints["left_wrist"], dtype=float)
                pos = (1.0 - alpha) * lw + alpha * p0
            else:
                pos = np.array([p0[0], 1.2 + alpha * (p0[1] - 1.2), p0[2]], dtype=float)
            f["ball_3d"] = [round(float(c), 4) for c in pos]
            f["ball_phase"] = "toss"

        elif contact_idx <= i <= bounce_idx:
            tau = t - t0
            bx = p0[0] + vx * tau
            by = max(0.0, p0[1] + vy0 * tau - 0.5 * g * tau * tau)
            bz = p0[2] + vz * tau
            f["ball_3d"] = [round(float(bx), 4), round(float(by), 4), round(float(bz), 4)]
            f["ball_phase"] = "flight"

        elif bounce_idx < i <= bounce_idx + int(0.6 * fps):
            tau_reb = t - t1
            bx = p1[0] + 0.85 * vx * tau_reb
            by = max(0.0, vy_rebound * tau_reb - 0.5 * g * tau_reb * tau_reb)
            bz = p1[2] + 0.85 * vz * tau_reb
            f["ball_3d"] = [round(float(bx), 4), round(float(by), 4), round(float(bz), 4)]
            f["ball_phase"] = "rebound"
        else:
            f["ball_3d"] = None
            f["ball_phase"] = None


def calibrate_and_export(
    video_path="Videos/tennis4.mp4",
    tracking_json="results/tennis4_tracking.json",
    output_video="results/tennis4_court_overlay.mp4",
    output_opengl_json="results/tennis4_opengl.json",
):
    with open(tracking_json, "r") as f:
        data = json.load(f)
    frames = data["frames"]
    fps = float(data["fps"])

    cap = cv2.VideoCapture(video_path)
    ret, first_frame = cap.read()
    if not ret:
        raise RuntimeError(f"Cannot read {video_path}")

    # 1. Click 8 points across Near Baseline, Net, Far Service Line, and Far Baseline
    clicked_px = click_court_keypoints(first_frame)
    H_court_to_px, _ = cv2.findHomography(CALIB_COURT_PTS_M, clicked_px, method=0)
    H_px_to_court = np.linalg.inv(H_court_to_px)

    reproj_px = cv2.perspectiveTransform(CALIB_COURT_PTS_M.reshape(-1, 1, 2), H_court_to_px).reshape(-1, 2)
    mean_err_px = float(np.mean(np.linalg.norm(reproj_px - clicked_px, axis=1)))
    print(f"[Calibration] 8-point homography computed (mean reprojection error: {mean_err_px:.2f} px)")

    # 2. Compute Player Pixel-to-Meter Scale & Lift Every Frame's Skeleton to 3D Court Space
    px_heights = []
    for f_data in frames:
        kps = f_data.get("player_keypoints_2d")
        if kps and kps["nose"][1] > 0 and kps["left_ankle"][1] > 0:
            ankle_y = max(kps["left_ankle"][1], kps["right_ankle"][1])
            px_heights.append((ankle_y - kps["nose"][1]) * 1.14)

    ref_px_height = float(np.percentile(px_heights, 85)) if px_heights else 300.0
    scale_m_per_px = 1.78 / ref_px_height

    for f_data in frames:
        f_data["player_joints_3d"] = lift_player_to_court_3d(
            f_data.get("player_keypoints_2d"),
            scale_m_per_px,
            anchor_3d=(0.0, 0.0, BASELINE_Z),
        )

    # 3. Detect Contact & Bounce Frames, Map Bounce to Court Meters, and Reconstruct 3D Ball Arc
    contact_idx, bounce_idx = find_contact_and_bounce_frames(frames)
    bounce_info = None

    if bounce_idx is not None:
        bx_px, by_px = frames[bounce_idx]["ball_2d"]["center"]
        pt_px = np.array([[[bx_px, by_px]]], dtype=np.float32)
        bx_m, bz_m = cv2.perspectiveTransform(pt_px, H_px_to_court)[0][0]

        # Check if serve landed IN the far singles service box (Z in [-6.40, 0], |X| <= 4.115)
        is_in = bool((-SERVICE_LINE_Z <= bz_m <= 0.0) and (abs(bx_m) <= SINGLES_HALF_W))
        bounce_info = {
            "frame": int(bounce_idx),
            "time": round(float(bounce_idx / fps), 4),
            "pixel": [round(float(bx_px), 1), round(float(by_px), 1)],
            "court_3d": [round(float(bx_m), 3), 0.0, round(float(bz_m), 3)],
            "in_bounds": is_in,
        }
        print(f"[Contact] Frame #{contact_idx} | [Bounce] Frame #{bounce_idx} -> Court (X={bx_m:.2f}m, Z={bz_m:.2f}m) | {'IN' if is_in else 'OUT'}")

        reconstruct_3d_ball_arc(frames, fps, contact_idx, bounce_idx, bounce_info["court_3d"])

    # 4. Render Video with Projected Court Grid & Bounce Marker
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    writer = cv2.VideoWriter(output_video, cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))

    for i, f_data in enumerate(frames):
        ret, frame = cap.read()
        if not ret:
            break

        vis = draw_projected_court(frame, H_court_to_px)
        vis = draw_player_skeleton(vis, f_data.get("player_keypoints_2d"))


        if f_data["ball_2d"] is not None:
            cx, cy = int(f_data["ball_2d"]["center"][0]), int(f_data["ball_2d"]["center"][1])
            cv2.circle(vis, (cx, cy), 8, (0, 255, 255), -1)

        if bounce_info is not None and i >= bounce_info["frame"]:
            bx, by = int(bounce_info["pixel"][0]), int(bounce_info["pixel"][1])
            ring_color = (0, 255, 0) if bounce_info["in_bounds"] else (0, 0, 255)
            label = "IN" if bounce_info["in_bounds"] else "OUT"
            cv2.circle(vis, (bx, by), 14, ring_color, 3)
            cv2.putText(vis, f"BOUNCE ({label})", (bx + 16, by + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, ring_color, 2)

        writer.write(vis)

    cap.release()
    writer.release()

    # 5. Export Complete 3D OpenGL Scene JSON
    opengl_payload = {
        "video": video_path,
        "fps": round(fps, 2),
        "total_frames": len(frames),
        "contact_frame": int(contact_idx) if contact_idx is not None else None,
        "court_3d": {
            "singles_half_width": SINGLES_HALF_W,
            "doubles_half_width": DOUBLES_HALF_W,
            "service_line_z": SERVICE_LINE_Z,
            "baseline_z": BASELINE_Z,
            "net_height_center": NET_HEIGHT_CENTER,
            "net_height_post": NET_HEIGHT_POST,
            "server_spawn_3d": [0.0, 0.0, BASELINE_Z],
            "lines_xz": COURT_LINES_M,
        },
        "skeleton_bones": BONES,
        "bounce": bounce_info,
        "frames": frames,
    }

    with open(output_opengl_json, "w") as f:
        json.dump(opengl_payload, f, indent=2)

    print(f"[OK] Saved full-court overlay video -> {output_video}")
    print(f"[OK] Saved ready-to-render 3D OpenGL JSON -> {output_opengl_json}")

def draw_player_skeleton(frame, pts_2d):
    """Draws the 2D player skeleton bones and keypoints onto the video frame."""
    if not pts_2d:
        return frame

    vis = frame.copy()
    # Draw bones (excluding synthetic neck/head_center which aren't in 2D keypoints)
    for joint_a, joint_b in BONES[:-1]:
        pt_a = pts_2d.get(joint_a)
        pt_b = pts_2d.get(joint_b)
        if pt_a and pt_b and pt_a[0] > 0 and pt_b[0] > 0:
            p1 = (int(round(pt_a[0])), int(round(pt_a[1])))
            p2 = (int(round(pt_b[0])), int(round(pt_b[1])))
            cv2.line(vis, p1, p2, (255, 200, 0), 2, cv2.LINE_AA)

    # Draw joint dots
    for name, pt in pts_2d.items():
        if pt and pt[0] > 0 and pt[1] > 0:
            cx, cy = int(round(pt[0])), int(round(pt[1]))
            cv2.circle(vis, (cx, cy), 4, (0, 255, 128), -1, cv2.LINE_AA)

    return vis



if __name__ == "__main__":
    calibrate_and_export()
