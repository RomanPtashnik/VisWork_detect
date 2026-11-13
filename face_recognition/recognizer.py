import os
import cv2
import insightface

class ArcFaceRecognizer:
    def __init__(self, ctx_id=-1):
        # Путь к модели внутри вашего проекта
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        model_path = os.path.join(project_root, "models", "buffalo_l", "w600k_r50.onnx")
        
        if not os.path.exists(model_path):
            raise RuntimeError(
                f"Model file not found: {model_path}\n"
                f"Please download buffalo_l.zip from\n"
                f"https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip\n"
                f"and extract it to {os.path.join(project_root, 'models', 'buffalo_l')}"
            )
        
        self.model = insightface.model_zoo.get_model(model_path)
        if self.model is None:
            raise RuntimeError(f"Failed to load model from {model_path}")
        
        self.model.prepare(ctx_id=ctx_id)
        print(f"ArcFace model loaded from {model_path}")

    def get_embedding(self, face_img):
        """
        Извлекает эмбеддинг (вектор признаков) из изображения лица.
        
        Args:
            face_img: numpy array (BGR) - вырезанная область лица.
            
        Returns:
            list: Вектор эмбеддинга размерностью 512.
        """
        # 1. Конвертируем BGR → RGB (модель обучена на RGB)
        face_rgb = cv2.cvtColor(face_img, cv2.COLOR_BGR2RGB)
        
        # 2. Изменяем размер до 112x112, так как модель ожидает вход такого размера
        face_resized = cv2.resize(face_rgb, (112, 112))
        
        # 3. Вызываем метод get_feat. Он может принимать как одно изображение, так и список.
        #    Возвращает массив формы (1, 512) для одного изображения.
        embedding = self.model.get_feat(face_resized)
        
        # 4. Превращаем numpy-массив в плоский список для сохранения в БД
        return embedding.flatten().tolist()