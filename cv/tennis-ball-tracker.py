from ultralytics import YOLO

#Testbench to see how well a model is identifying a tennis ball in of a video

#model = YOLO('yolov8x.pt')
model = YOLO('training/yolo11s.pt')

results = model.predict(
    'Videos/tennis3.mp4',
    classes=[29, 32],  
    conf=0.20,         
    imgsz=1280,        
    device='mps',      
    save=True,
    project='/Users/christophmissall/Desktop/Tennis_334/TennisVisualizer',  
    name='results',   
    exist_ok=False,     
    stream=True,       
)

for frame_idx, r in enumerate(results):
    if len(r.boxes) > 0:
        print(f"Frame {frame_idx}:")
        for box in r.boxes:
            cls_id = int(box.cls[0])
            conf = float(box.conf[0])
            xyxy = box.xyxy[0].tolist()
            print(f"  {model.names[cls_id]} ({conf:.2f}): {xyxy}")
