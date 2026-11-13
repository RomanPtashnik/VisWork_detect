import cv2

class YuNetDetector:
    def __init__(self, model_path, input_size=(320, 320), conf_threshold=0.6, nms_threshold=0.3):
        self.model = cv2.FaceDetectorYN.create(
            model=model_path,
            config="",
            input_size=input_size,
            score_threshold=conf_threshold,
            nms_threshold=nms_threshold,
            top_k=5000,
            backend_id=cv2.dnn.DNN_BACKEND_OPENCV,
            target_id=cv2.dnn.DNN_TARGET_CPU
        )

    def detect(self, image):
        h, w = image.shape[:2]
        self.model.setInputSize((w, h))
        _, faces = self.model.detect(image)
        if faces is None:
            return []
        bboxes = []
        for face in faces:
            x, y, w, h = face[:4].astype(int)
            bboxes.append((x, y, w, h))
        return bboxes