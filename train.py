from ultralytics import YOLO

model = YOLO("yolo11n.pt") 

results = model.train(data="../grocery_dataset_2/data.yaml", epochs=125, imgsz=640, device="mps", plots=False)

model.save("trained_yolo_model.pt")

