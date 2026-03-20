# Retinal_blindness_detection_Pytorch-master

Here is a **clean, detailed, professional README** you can use for your GitHub project. I improved structure, clarity, and added missing sections like setup, usage, and architecture.

---

# Retinal Blindness Detection using Deep Learning (PyTorch)

## Overview

This project focuses on early detection of **Diabetic Retinopathy (DR)** using deep learning on retinal fundus images. DR is a major cause of blindness in working-age adults, and early screening reduces vision loss significantly. ([GitHub][1])

The system uses a **pretrained CNN model (ResNet152)** to classify retinal images into severity levels from 0 to 4. The solution includes training, inference, GUI interface, and notification support.

---

## Problem Statement

Diabetic Retinopathy progresses silently and requires early diagnosis. Manual screening demands skilled ophthalmologists and time. Automated image analysis helps:

* Reduce diagnostic time
* Support doctors in decision-making
* Enable large-scale screening in rural areas
* Lower healthcare costs ([GitHub][1])

---

## Key Features

* Deep learning classification using PyTorch
* Multi-class prediction (0–4 severity levels)
* Image preprocessing and augmentation
* GUI-based prediction system using Tkinter
* Database integration for storing results
* SMS notification using Twilio API
* Notebook-based training and inference

---

## Dataset

* **APTOS 2019 Blindness Detection Dataset (Kaggle)**
* Retinal fundus images labeled from:

  * 0 → No DR
  * 1 → Mild
  * 2 → Moderate
  * 3 → Severe
  * 4 → Proliferative DR ([Medium][2])

---

## Model Architecture

* Backbone: **ResNet152 (Pretrained CNN)**
* Transfer learning applied for feature extraction
* Final layers modified for 5-class classification
* Training performed over 100+ epochs for convergence ([GitHub][1])

---

## Project Structure

```
├── images/                     # Training images  
├── sampleimages/              # Sample test images  
├── training.ipynb             # Model training notebook  
├── inference.ipynb            # Batch inference  
├── Single_test_inference.ipynb# Single image prediction  
├── model.py                   # Model architecture  
├── blindness.py               # Main execution script  
├── send_sms.py                # SMS notification logic  
├── requirements.txt           # Dependencies  
├── README.md                  # Project documentation  
```

---

## Data Preprocessing

* Image resizing
* Noise reduction (Gaussian blur)
* Circular cropping for retina focus
* Brightness and contrast enhancement
* Data augmentation:

  * Rotation
  * Flip
  * Zoom
  * Cropping

These steps improve model generalization and reduce overfitting.

---

## Training Process

* Input images processed to fixed size
* Data augmentation applied
* Transfer learning with ResNet152
* Loss optimization using backpropagation
* Model evaluated using classification metrics

---

## Inference Pipeline

1. Load trained model
2. Input retinal image
3. Apply preprocessing
4. Run prediction
5. Output DR severity level
6. Store result in database
7. Send SMS notification (optional)

---

## GUI System

* Built using Tkinter
* User uploads retinal image
* Displays prediction result
* Stores patient data and results

---

## Technologies Used

| Category      | Tools            |
| ------------- | ---------------- |
| Deep Learning | PyTorch          |
| Programming   | Python           |
| GUI           | Tkinter          |
| Database      | MySQL (HeidiSQL) |
| API           | Twilio           |
| Data Handling | NumPy, Pandas    |

---

## Results

* Achieved high classification accuracy after extensive training
* Improved robustness using augmentation techniques
* Reduced manual screening effort
* Enabled real-time prediction through GUI

---

## Future Improvements

* Convert system into web application
* Use lightweight models for faster inference
* Add privacy-preserving techniques (federated learning)
* Improve false negative reduction (critical in healthcare)
* Enable multi-user concurrency support
* Deploy on cloud for scalability

---

## How to Run

### 1. Clone Repository

```bash
git clone https://github.com/gowrishgalaxy/Retinal_blindness_detection_Pytorch-master
cd Retinal_blindness_detection_Pytorch-master
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Training

```bash
jupyter notebook training.ipynb
```

### 4. Run Inference

```bash
jupyter notebook inference.ipynb
```

### 5. Run GUI

```bash
python blindness.py
```

---

## Applications

* Hospitals and diagnostic centers
* Rural healthcare screening
* Telemedicine systems
* AI-assisted ophthalmology

---

## Contribution

Contributions are welcome. Fork the repository and submit pull requests for improvements.

---

## License

No license specified in original repository.

---

If you want, I will convert this into:
• Resume project description (short bullets)
• Portfolio version
• LinkedIn project post
• Viva explanation (step-by-step)

[1]: https://github.com/souravs17031999/Retinal_blindness_detection_Pytorch?utm_source=chatgpt.com "souravs17031999/Retinal_blindness_detection_Pytorch"
[2]: https://medium.com/data-science/blindness-detection-diabetic-retinopathy-using-deep-learning-on-eye-retina-images-baf20fcf409e?utm_source=chatgpt.com "Blindness detection (Diabetic retinopathy) using Deep ..."
