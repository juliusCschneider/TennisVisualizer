#original testbench to check the pose estimation

from ultralytics import YOLO

model = YOLO("yolo26m-pose.pt")

results = model.predict("Videos/tennis1.mp4", save = True, show = True)

