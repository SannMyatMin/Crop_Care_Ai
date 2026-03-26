import os
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.preprocessing import image

class PaddyDiseaseDataProcessor:
    def __init__(self, dataset_dir="paddy_disease_classification", img_size=224):
        self.dataset_dir = dataset_dir
        self.csv         = os.path.join(self.dataset_dir, "train.csv")
        self.train_ds    = None
        self.val_ds      = None
        
