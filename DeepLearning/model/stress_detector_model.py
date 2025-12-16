"""
Modelo de Deep Learning para Detección de Estrés
Adaptado para dataset de Roboflow con formato CSV
"""

import numpy as np
import pandas as pd
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers, models
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.callbacks import EarlyStopping, ReduceLROnPlateau, ModelCheckpoint
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import cv2
from pathlib import Path
import os

class StressDetector:
    """
    Detector de estrés usando CNN con Transfer Learning
    Dataset: Non-Stress vs Stress (clasificación binaria)
    """
    
    def __init__(self, img_size=(224, 224)):
        """
        Args:
            img_size: Tamaño de las imágenes de entrada (alto, ancho)
        """
        self.img_size = img_size
        self.num_classes = 2  # Non-Stress y Stress
        self.model = None
        self.history = None
        
        # Mapeo de clases
        self.class_labels = {
            0: 'Non-Stress',
            1: 'Stress'
        }
        
    def load_data_from_csv(self, data_dir, csv_file='_classes.csv'):
        """
        Carga las imágenes y labels desde el CSV de Roboflow
        
        Args:
            data_dir: Directorio con las imágenes y el CSV
            csv_file: Nombre del archivo CSV
            
        Returns:
            images, labels, filenames
        """
        # Normalizar ruta para compatibilidad Windows/Linux
        data_dir = os.path.normpath(data_dir)
        csv_path = os.path.join(data_dir, csv_file)
        
        # Verificar que exista el directorio
        if not os.path.exists(data_dir):
            raise FileNotFoundError(
                f"\n ERROR: No se encontró el directorio '{data_dir}'\n"
                f"   Asegúrate de tener la estructura:\n"
                f"   data2/\n"
                f"   ├── train/\n"
                f"   ├── valid/\n"
                f"   └── test/\n"
            )
        
        # Verificar que exista el CSV
        if not os.path.exists(csv_path):
            raise FileNotFoundError(
                f"\n ERROR: No se encontró el archivo '{csv_path}'\n"
                f"   Archivos en '{data_dir}':\n" +
                "\n".join(f"   - {f}" for f in os.listdir(data_dir)[:10])
            )
        
        df = pd.read_csv(csv_path)
        
        images = []
        labels = []
        filenames = []
        skipped = {'not_found': 0, 'load_error': 0, 'invalid_label': 0}
        
        print(f"\n Cargando datos desde: {data_dir}")
        print(f"   Total de imágenes en CSV: {len(df)}")
        
        for idx, row in df.iterrows():
            img_path = os.path.join(data_dir, row['filename'])
            
            if not os.path.exists(img_path):
                skipped['not_found'] += 1
                if skipped['not_found'] <= 3:
                    print(f"  Imagen no encontrada: {img_path}")
                continue
            
            # Interpretar label correctamente
            # Non=0, Stress=1 → label=1 (Stress)
            # Non=1, Stress=0 → label=0 (Non-Stress)
            # Non=0, Stress=0 → inválido (skip)
            # Non=1, Stress=1 → ambiguo (skip)
            
            non_val = row['Non']
            stress_val = row['Stress']
            
            # Validar combinación
            if non_val == 0 and stress_val == 1:
                label = 1  # Stress
            elif non_val == 1 and stress_val == 0:
                label = 0  # Non-Stress
            else:
                # Caso inválido o ambiguo
                skipped['invalid_label'] += 1
                if skipped['invalid_label'] <= 3:
                    print(f"  Label inválido (Non={non_val}, Stress={stress_val}): {row['filename']}")
                continue
            
            # Cargar imagen
            img = cv2.imread(img_path)
            if img is None:
                skipped['load_error'] += 1
                if skipped['load_error'] <= 3:
                    print(f"  Error al cargar: {img_path}")
                continue
                
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, self.img_size)
            
            images.append(img)
            labels.append(label)
            filenames.append(row['filename'])
        
        images = np.array(images, dtype=np.float32) / 255.0
        labels = np.array(labels)
        
        # Mostrar imágenes saltadas
        if sum(skipped.values()) > 0:
            print(f"\n  Imágenes saltadas:")
            if skipped['not_found'] > 0:
                print(f"   - No encontradas: {skipped['not_found']}")
            if skipped['load_error'] > 0:
                print(f"   - Error al cargar: {skipped['load_error']}")
            if skipped['invalid_label'] > 0:
                print(f"   - Labels inválidos/ambiguos: {skipped['invalid_label']}")
        
        # Estadísticas
        non_stress = np.sum(labels == 0)
        stress = np.sum(labels == 1)
        total = len(labels)
        
        print(f"\n Estadísticas del conjunto:")
        print(f"   Total cargado: {total}")
        print(f"   Non-Stress: {non_stress} ({non_stress/total*100:.1f}%)")
        print(f"   Stress: {stress} ({stress/total*100:.1f}%)")
        
        return images, labels, filenames
    
    def build_model(self, use_transfer_learning=True):
        """
        Construye el modelo CNN con o sin Transfer Learning
        """
        if use_transfer_learning:
            # Usar MobileNetV2 preentrenado (eficiente)
            base_model = MobileNetV2(
                input_shape=(*self.img_size, 3),
                include_top=False,
                weights='imagenet'
            )
            
            # Congelar las capas base inicialmente
            base_model.trainable = False
            
            # Construir el modelo completo
            inputs = keras.Input(shape=(*self.img_size, 3))
            
            # Preprocesamiento para MobileNetV2
            x = keras.applications.mobilenet_v2.preprocess_input(inputs)
            
            # Base model
            x = base_model(x, training=False)
            
            # Capas personalizadas para clasificación binaria
            x = layers.GlobalAveragePooling2D()(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(0.5)(x)
            x = layers.Dense(256, activation='relu')(x)
            x = layers.BatchNormalization()(x)
            x = layers.Dropout(0.3)(x)
            x = layers.Dense(128, activation='relu')(x)
            x = layers.Dropout(0.2)(x)
            # Para clasificación binaria: 1 neurona con sigmoid
            outputs = layers.Dense(1, activation='sigmoid')(x)
            
            self.model = keras.Model(inputs, outputs)
            
        else:
            # Modelo CNN desde cero
            self.model = models.Sequential([
                # Bloque 1
                layers.Conv2D(64, (3, 3), activation='relu', 
                            input_shape=(*self.img_size, 3)),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Bloque 2
                layers.Conv2D(128, (3, 3), activation='relu'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Bloque 3
                layers.Conv2D(256, (3, 3), activation='relu'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Bloque 4
                layers.Conv2D(512, (3, 3), activation='relu'),
                layers.BatchNormalization(),
                layers.MaxPooling2D((2, 2)),
                layers.Dropout(0.25),
                
                # Clasificador
                layers.Flatten(),
                layers.Dense(512, activation='relu'),
                layers.BatchNormalization(),
                layers.Dropout(0.5),
                layers.Dense(256, activation='relu'),
                layers.Dropout(0.3),
                # Clasificación binaria
                layers.Dense(1, activation='sigmoid')
            ])
        
        print("\n  Modelo construido exitosamente")
        return self.model
    
    def compile_model(self, learning_rate=0.001):
        """
        Compila el modelo con optimizador y métricas para clasificación binaria
        """
        self.model.compile(
            optimizer=keras.optimizers.Adam(learning_rate=learning_rate),
            loss='binary_crossentropy',  # Para clasificación binaria
            metrics=[
                'accuracy',
                keras.metrics.Precision(name='precision'),
                keras.metrics.Recall(name='recall'),
                keras.metrics.AUC(name='auc')
            ]
        )
        
        print("\n Resumen del modelo:")
        self.model.summary()
    
    def train(self, X_train, y_train, X_val, y_val, epochs=50, 
              batch_size=32, checkpoint_path='best_stress_model.h5'):
        """
        Entrena el modelo con callbacks
        """
        # Calcular class weights para manejar desbalance
        from sklearn.utils.class_weight import compute_class_weight
        
        class_weights = compute_class_weight(
            'balanced',
            classes=np.unique(y_train),
            y=y_train
        )
        class_weight_dict = {i: class_weights[i] for i in range(len(class_weights))}
        
        print(f"\n  Class weights: {class_weight_dict}")
        
        callbacks = [
            EarlyStopping(
                monitor='val_loss',
                patience=15,
                restore_best_weights=True,
                verbose=1
            ),
            ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.5,
                patience=7,
                min_lr=1e-7,
                verbose=1
            ),
            ModelCheckpoint(
                checkpoint_path,
                monitor='val_accuracy',
                save_best_only=True,
                verbose=1
            )
        ]
        
        print(f"\n Iniciando entrenamiento...")
        print(f"   Epochs: {epochs}")
        print(f"   Batch size: {batch_size}")
        print(f"   Train samples: {len(X_train)}")
        print(f"   Validation samples: {len(X_val)}")
        
        self.history = self.model.fit(
            X_train, y_train,
            validation_data=(X_val, y_val),
            epochs=epochs,
            batch_size=batch_size,
            class_weight=class_weight_dict,
            callbacks=callbacks,
            verbose=1
        )
        
        print("\n Entrenamiento completado!")
        return self.history
    
    def plot_training_history(self, save_path='training_history.png'):
        """
        Visualiza el historial de entrenamiento
        """
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Train', linewidth=2)
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation', linewidth=2)
        axes[0, 0].set_title('Model Accuracy', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        axes[0, 0].grid(True, alpha=0.3)
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Train', linewidth=2)
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation', linewidth=2)
        axes[0, 1].set_title('Model Loss', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        axes[0, 1].grid(True, alpha=0.3)
        
        # Precision
        axes[1, 0].plot(self.history.history['precision'], label='Train', linewidth=2)
        axes[1, 0].plot(self.history.history['val_precision'], label='Validation', linewidth=2)
        axes[1, 0].set_title('Model Precision', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch')
        axes[1, 0].set_ylabel('Precision')
        axes[1, 0].legend()
        axes[1, 0].grid(True, alpha=0.3)
        
        # Recall
        axes[1, 1].plot(self.history.history['recall'], label='Train', linewidth=2)
        axes[1, 1].plot(self.history.history['val_recall'], label='Validation', linewidth=2)
        axes[1, 1].set_title('Model Recall', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch')
        axes[1, 1].set_ylabel('Recall')
        axes[1, 1].legend()
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n Gráfica guardada en: {save_path}")
        plt.show()
    
    def evaluate(self, X_test, y_test, save_path='confusion_matrix.png'):
        """
        Evalúa el modelo y muestra métricas detalladas
        """
        print("\n Evaluando modelo en conjunto de prueba...")
        
        # Predicciones
        predictions = self.model.predict(X_test, verbose=0)
        y_pred = (predictions > 0.5).astype(int).flatten()
        
        # Métricas generales
        test_loss, test_acc, test_prec, test_rec, test_auc = self.model.evaluate(
            X_test, y_test, verbose=0
        )
        
        print(f"\n Métricas en Test Set:")
        print(f"   Accuracy:  {test_acc:.4f}")
        print(f"   Precision: {test_prec:.4f}")
        print(f"   Recall:    {test_rec:.4f}")
        print(f"   AUC:       {test_auc:.4f}")
        print(f"   Loss:      {test_loss:.4f}")
        
        # Classification Report
        print("\n" + "="*50)
        print("CLASSIFICATION REPORT")
        print("="*50)
        print(classification_report(
            y_test, y_pred,
            target_names=['Non-Stress', 'Stress'],
            digits=4
        ))
        
        # Confusion Matrix
        cm = confusion_matrix(y_test, y_pred)
        
        plt.figure(figsize=(8, 6))
        sns.heatmap(
            cm,
            annot=True,
            fmt='d',
            cmap='Blues',
            xticklabels=['Non-Stress', 'Stress'],
            yticklabels=['Non-Stress', 'Stress'],
            cbar_kws={'label': 'Count'}
        )
        plt.title('Confusion Matrix - Stress Detection', fontsize=14, fontweight='bold')
        plt.ylabel('True Label')
        plt.xlabel('Predicted Label')
        plt.tight_layout()
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        print(f"\n Matriz de confusión guardada en: {save_path}")
        plt.show()
        
        return y_pred, predictions
    
    def predict_stress(self, image_path):
        """
        Predice el nivel de estrés de una imagen
        
        Args:
            image_path: Ruta a la imagen
            
        Returns:
            dict con predicción y confianza
        """
        # Cargar y preprocesar imagen
        img = cv2.imread(str(image_path))
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        img_resized = cv2.resize(img, self.img_size)
        img_array = np.expand_dims(img_resized, axis=0) / 255.0
        
        # Predicción
        prediction = self.model.predict(img_array, verbose=0)[0][0]
        
        stress_detected = prediction > 0.5
        confidence = prediction if stress_detected else (1 - prediction)
        
        result = {
            'stress_detected': bool(stress_detected),
            'label': 'Stress' if stress_detected else 'Non-Stress',
            'confidence': float(confidence),
            'raw_score': float(prediction)
        }
        
        return result
    
    def predict_with_face_detection(self, image_path):
        """
        Detecta rostros y predice nivel de estrés
        """
        # Cargar detector de rostros de OpenCV
        face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        img = cv2.imread(str(image_path))
        if img is None:
            raise ValueError(f"No se pudo cargar la imagen: {image_path}")
            
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        
        # Detectar rostros
        faces = face_cascade.detectMultiScale(
            gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
        )
        
        results = []
        
        for (x, y, w, h) in faces:
            # Extraer ROI del rostro
            face_roi = img[y:y+h, x:x+w]
            face_rgb = cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB)
            face_resized = cv2.resize(face_rgb, self.img_size)
            face_array = np.expand_dims(face_resized, axis=0) / 255.0
            
            # Predicción
            prediction = self.model.predict(face_array, verbose=0)[0][0]
            stress_detected = prediction > 0.5
            confidence = prediction if stress_detected else (1 - prediction)
            
            label = 'Stress' if stress_detected else 'Non-Stress'
            
            results.append({
                'bbox': (x, y, w, h),
                'label': label,
                'stress_detected': stress_detected,
                'confidence': float(confidence)
            })
            
            # Dibujar en la imagen
            color = (0, 255, 0) if not stress_detected else (255, 0, 0)
            
            cv2.rectangle(img, (x, y), (x+w, y+h), color, 2)
            
            text = f"{label} ({confidence:.2f})"
            cv2.putText(img, text, (x, y-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, color, 2)
        
        return results, img
    
    def save_model(self, filepath='stress_model.h5'):
        """Guarda el modelo entrenado"""
        self.model.save(filepath)
        print(f"\n Modelo guardado en: {filepath}")
    
    def load_model(self, filepath='stress_model.h5'):
        """Carga un modelo previamente entrenado"""
        self.model = keras.models.load_model(filepath)
        print(f"\n Modelo cargado desde: {filepath}")


# Función auxiliar para cargar todos los conjuntos de datos
def load_all_datasets(data_root='data2'):
    """
    Carga train, valid y test desde el directorio raíz
    """
    detector = StressDetector()
    
    # Cargar datos
    X_train, y_train, _ = detector.load_data_from_csv(os.path.join(data_root, 'train'))
    X_val, y_val, _ = detector.load_data_from_csv(os.path.join(data_root, 'valid'))
    X_test, y_test, _ = detector.load_data_from_csv(os.path.join(data_root, 'test'))
    
    return (X_train, y_train), (X_val, y_val), (X_test, y_test)