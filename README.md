# Accident Detection System

This project is an enhanced accident detection system with a real-time web and mobile application for alerting and monitoring accidents. It integrates sensor data, machine learning models, a mobile app for on-the-go monitoring, and a frontend dashboard for improved usability and road safety.

## Features

- **Real-time Accident Detection**: Leverages accelerometer and gyroscope data to identify accidents.
- **Mobile Application**:
  - Developed using Android Studio for on-the-go monitoring.
  - Provides accident alerts and updates on hospital bed availability.
- **Web Application**:
  - Built with React for visualizing accident data.
  - Features bed availability updates and alert notifications.
- **Machine Learning Models**: Includes pretrained Dense Neural Network and Isolation Forest models.
- **Comprehensive Dataset**: Updated and extensive datasets for training and testing.
- **Backend Functionality**: Scripts for processing data, integrating alerts, and backend operations.

## Repository Structure

- **`App/`**: Android-based mobile application files.
  - `MainActivity.java`: Entry point of the application.
  - `ui/home/`: Home screen of the application.
  - `ui/dashboard/`: Dashboard for accident monitoring.
  - `ui/notifications/`: Notification center for updates.
- **`Trained model/`**: Contains pretrained machine learning models.
- **`Phones_accelerometer_reduced/` and `Phones_gyroscope_reduced/`**: Reduced accelerometer and gyroscope datasets.
- **`gps_dataset/`**: GPS datasets for training, controlled testing, and uncontrolled testing.
- **`Test/`**: Backend scripts for database integration and testing.
- **`webpage/`**: React-based frontend application files.
- **Python Scripts**:
  - `integrate_and_post_alert.py`: Combines detection results and posts alerts.
  - `acquire_bed.py`: Estimates hospital bed availability.
  - `backend_isolation_only.py`: Backend operations using Isolation Forest model.
  - `convert.py`: Utility for data preprocessing.

## Installation

### Backend Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/anandharshit712/Accident_Detection_System.git
   cd Accident_Detection_System
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run backend scripts:
   ```bash
   python integrate_and_post_alert.py
   ```

### Frontend Setup (Web Application)

1. Navigate to the `webpage/` directory:
   ```bash
   cd webpage
   ```

2. Install React dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

### Mobile App Setup

1. Navigate to the `App/` directory and open it in Android Studio.

2. Build the project to install dependencies.

3. Run the app on an emulator or physical device.

## Usage

1. **Run Backend**:
   - Execute backend scripts to process sensor data and detect accidents.

2. **Use Frontend**:
   - Open the React web application to view accident alerts and hospital bed availability.

3. **Use Mobile App**:
   - Launch the mobile app for on-the-go access to accident alerts and hospital data.

4. **Analyze Results**:
   - Use pretrained models or retrain with the provided datasets for improved detection.

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
