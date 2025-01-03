# Accident Detection System

This project provides an accident detection system leveraging sensor data, trained models, and backend processing for real-time detection. It aims to improve road safety by analyzing accelerometer and gyroscope data to identify potential accidents.

## Features

- **Real-time Processing**: Detects accidents based on accelerometer and gyroscope data.
- **Machine Learning Models**: Includes pretrained models like Dense Neural Networks and Isolation Forests.
- **Comprehensive Dataset**: Contains training and test datasets for GPS, accelerometer, and gyroscope data.
- **Backend Functionality**: Backend scripts for data processing and database integration.

## Repository Structure

- **`Trained model/`**: Contains pretrained models, including:
  - `dense_autoencoder_model_Dense_NN.pkl`
  - `isolation_forest_model.pkl`
- **`Phones_accelerometer_reduced/`**: Reduced accelerometer datasets.
- **`Phones_gyroscope_reduced/`**: Reduced gyroscope datasets.
- **`gps_dataset/`**: GPS datasets for training, controlled testing, and uncontrolled testing.
- **`Test/`**: Backend and database connection scripts for testing.
- **Python Scripts**:
  - `convert.py`: Data conversion utilities.
  - `process_all_user_dense_NN.py`: Process data using Dense Neural Network.
  - `backend_isolation_only.py`: Backend processing with Isolation Forest.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/anandharshit712/Accident_Detection_System.git
   cd Accident_Detection_System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(If `requirements.txt` is missing, install necessary packages manually based on the code, e.g., `pandas`, `scikit-learn`, etc.)*

## Usage

1. **Preprocess Data**:
   - Use scripts like `convert.py` or `process_all_user_dense_NN.py` to preprocess data.

2. **Run Backend Scripts**:
   - Execute backend scripts in the `Test` directory to process data and integrate with the database.

3. **Analyze Results**:
   - Use pretrained models or retrain using the provided datasets.

## Datasets

- **Training Data**:
  - Accelerometer: `Phones_accelerometer.csv`
  - Gyroscope: `Phones_gyroscope.csv`
  - GPS: `gps_dataset/dataset_training`
- **Testing Data**:
  - Controlled Tests: `gps_dataset/dataset_controlled_test`
  - Uncontrolled Tests: `gps_dataset/dataset_uncontrolled_test`

## Contributing

Contributions are welcome! Open an issue or submit a pull request for suggestions or improvements.
