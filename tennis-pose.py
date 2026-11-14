from ultralytics import YOLO

model = YOLO("yolo26m-pose.pt")

results = model.predict("tennis1.mp4", save = True, show = True)