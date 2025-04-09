import React, { useState, useEffect, useRef } from 'react';
import {
    View,
    Text,
    TextInput,
    Button,
    StyleSheet,
    PermissionsAndroid,
    ToastAndroid,
    Platform,
    Linking,
} from 'react-native';
import {
  accelerometer,
  gyroscope,
  setUpdateIntervalForType,
  SensorTypes,
} from 'react-native-sensors';
import Geolocation from '@react-native-community/geolocation';
import axios from 'axios';
import PushNotification from 'react-native-push-notification';
import AsyncStorage from '@react-native-async-storage/async-storage'; // ✅ Added

const BKL_TRACKER_URL = 'https://accident-cisl.onrender.com';
const CHANNEL_ID = 'accident_notifications';

interface SensorData {
    accelX: number;
    accelY: number;
    accelZ: number;
    gyroX: number;
    gyroY: number;
    gyroZ: number;
    latitude: number;
    longitude: number;
    speed: number;
}

interface AccidentData {
    lat: number;
    long: number;
    status?: boolean;
    no_of_beds?: number[];
}

const App = () => {
    const [ID, setID] = useState('');
    const [isSendingData, setIsSendingData] = useState(false);
    const [isEditing, setIsEditing] = useState(false);

    const [sensorData, setSensorData] = useState<SensorData>({
        accelX: 0,
        accelY: 0,
        accelZ: 0,
        gyroX: 0,
        gyroY: 0,
        gyroZ: 0,
        latitude: 0,
        longitude: 0,
        speed: 0,
    });

    const [accidentData, setAccidentData] = useState<AccidentData | null>(null);
    const [bedsNumber, setBedsNumber] = useState('');
    const [showBedsInput, setShowBedsInput] = useState(false);

    const sendingInterval = useRef<NodeJS.Timeout | null>(null);
    const accelerometersubscription = useRef<any>(null);
    const gyroscopesubscription = useRef<any>(null);
    const locationWatchId = useRef<number | null>(null);

    useEffect(() => {
        PushNotification.createChannel(
            {
                channelId: CHANNEL_ID,
                channelName: 'Accident Notifications',
                channelDescription: 'Notifications for nearby accidents',
                importance: 4,
                vibrate: true,
            },
            (created) => console.log(`Channel created: ${created}`)
        );

        requestPermissions();
        loadStoredMobileNumber(); // ✅ Load mobile number on launch

        return () => {
            accelerometersubscription.current?.unsubscribe();
            gyroscopesubscription.current?.unsubscribe();
            if (sendingInterval.current) clearInterval(sendingInterval.current);
            if (locationWatchId.current !== null) Geolocation.clearWatch(locationWatchId.current);
        };
    }, []);

    const loadStoredMobileNumber = async () => {
        try {
            const storedID = await AsyncStorage.getItem('mobileNumber');
            if (storedID) {
                setID(storedID);
            }
        } catch (error) {
            console.error('Failed to load mobile number:', error);
        }
    };

    const requestPermissions = async () => {
        try {
            if (Platform.OS === 'android') {
                const granted = await PermissionsAndroid.requestMultiple([
                    PermissionsAndroid.PERMISSIONS.ACCESS_FINE_LOCATION,
                    PermissionsAndroid.PERMISSIONS.ACCESS_COARSE_LOCATION,
                    PermissionsAndroid.PERMISSIONS.ACCESS_BACKGROUND_LOCATION,
                    PermissionsAndroid.PERMISSIONS.POST_NOTIFICATIONS,
                ]);

                const locationGranted =
                    granted['android.permission.ACCESS_FINE_LOCATION'] === PermissionsAndroid.RESULTS.GRANTED;

                if (locationGranted) {
                    startLocationUpdates();
                    fetchInitialLocation();
                } else {
                    console.warn('Location permission denied');
                }
            } else {
                startLocationUpdates();
                fetchInitialLocation();
            }

            startSensorUpdates();
        } catch (err) {
            console.warn('Permission error:', err);
        }
    };

    const fetchInitialLocation = () => {
        Geolocation.getCurrentPosition(
            (position) => {
                setSensorData((prev) => ({
                    ...prev,
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    speed: position.coords.speed || 0,
                }));
            },
            (error) => {
                ToastAndroid.show(`GPS Error: ${error.message}`, ToastAndroid.LONG);
                if (error.code === 2) {
                    Linking.openSettings();
                }
                if (error.code === 3) {
                    Geolocation.getCurrentPosition(
                        (pos) => {
                            setSensorData((prev) => ({
                                ...prev,
                                latitude: pos.coords.latitude,
                                longitude: pos.coords.longitude,
                                speed: pos.coords.speed || 0,
                            }));
                        },
                        (err2) => {
                            ToastAndroid.show('Retry failed. Check location settings.', ToastAndroid.LONG);
                        },
                        {
                            enableHighAccuracy: true,
                            timeout: 30000,
                            maximumAge: 1000,
                        }
                    );
                }
            },
            {
                enableHighAccuracy: true,
                timeout: 20000,
                maximumAge: 1000,
            }
        );
    };

    const startLocationUpdates = () => {
        locationWatchId.current = Geolocation.watchPosition(
            (position) => {
                setSensorData((prev) => ({
                    ...prev,
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude,
                    speed: position.coords.speed || 0,
                }));
            },
            (error) => console.warn('watchPosition error:', error.message),
            {
                enableHighAccuracy: true,
                distanceFilter: 0,
                interval: 2000,
                fastestInterval: 1000,
                useSignificantChanges: false,
            }
        );
    };

    const startSensorUpdates = () => {
        setUpdateIntervalForType(SensorTypes.accelerometer, 1000);
        setUpdateIntervalForType(SensorTypes.gyroscope, 1000);

        accelerometersubscription.current = accelerometer.subscribe(
            ({ x, y, z }) => {
                setSensorData((prev) => ({
                    ...prev,
                    accelX: x,
                    accelY: y,
                    accelZ: z,
                }));
            },
            (error) => console.warn('Accelerometer error:', error)
        );

        gyroscopesubscription.current = gyroscope.subscribe(
            ({ x, y, z }) => {
                setSensorData((prev) => ({
                    ...prev,
                    gyroX: x,
                    gyroY: y,
                    gyroZ: z,
                }));
            },
            (error) => console.warn('Gyroscope error:', error)
        );
    };

    const toggleDataSending = () => {
        if (isSendingData) {
            setIsSendingData(false);
            if (sendingInterval.current) clearInterval(sendingInterval.current);
        } else {
            if (ID.trim() === '') {
                ToastAndroid.show('Please enter mobile number', ToastAndroid.SHORT);
                return;
            }
            setIsSendingData(true);
            sendDataToServer();
            sendingInterval.current = setInterval(sendDataToServer, 1000);
        }
    };

    const sendDataToServer = async () => {
        try {
            await axios.post(`${BKL_TRACKER_URL}/upload_sensor_data`, {
                ID,
                ...sensorData,
            });
        } catch (error) {
            console.error('Error sending data:', error);
        }
    };

    useEffect(() => {
        const accidentCheckInterval = setInterval(fetchAccidentData, 2000);
        return () => clearInterval(accidentCheckInterval);
    }, []);

    const fetchAccidentData = async () => {
        try {
            const { data } = await axios.get(`${BKL_TRACKER_URL}/accident-status`);
            if (data) {
                setAccidentData(data);
                checkAccidentProximity(data);
            } else {
                setAccidentData(null);
                setShowBedsInput(false);
            }
        } catch (error) {
            if (axios.isAxiosError(error) && error.response?.status === 404) {
                setAccidentData(null);
                setShowBedsInput(false);
            } else {
                console.error('Error fetching accident data:', error);
            }
        }
    };

    const checkAccidentProximity = (accident: AccidentData) => {
        const distance = 400.0; // Replace with real formula if needed
        if (distance <= 500) {
            showAccidentNotification();
        }
    };

    const showAccidentNotification = () => {
        setShowBedsInput(true);
        PushNotification.localNotification({
            channelId: CHANNEL_ID,
            title: 'Accident Alert',
            message: 'An accident has been detected within 500 meters!',
            playSound: true,
            soundName: 'default',
            importance: 'high',
            vibrate: true,
        });
    };

    const sendBedsData = async () => {
        const beds = parseInt(bedsNumber, 10);
        if (isNaN(beds)) {
            ToastAndroid.show('Please enter a valid number of beds', ToastAndroid.SHORT);
            return;
        }

        try {
            await axios.post(`${BKL_TRACKER_URL}/beds`, {
                ...accidentData,
                status: true,
                no_of_beds: [beds],
            });

            ToastAndroid.show('Beds data sent successfully!', ToastAndroid.SHORT);
            setShowBedsInput(false);
            setBedsNumber('');
        } catch (error) {
            console.error('Error sending beds data:', error);
            ToastAndroid.show('Failed to send beds data', ToastAndroid.SHORT);
        }
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>BKL Tracker</Text>

            <View style={styles.inputContainer}>
                <TextInput
                    style={styles.input}
                    placeholder="Mobile Number"
                    value={ID}
                    onChangeText={setID}
                    editable={isEditing}
                    keyboardType="phone-pad"
                />
                <Button
                    title={isEditing ? 'Save' : 'Edit'}
                    onPress={async () => {
                        if (isEditing) {
                            try {
                                await AsyncStorage.setItem('mobileNumber', ID); // ✅ Save on "Save"
                                ToastAndroid.show('Mobile number saved', ToastAndroid.SHORT);
                            } catch (error) {
                                console.error('Failed to save mobile number:', error);
                            }
                        }
                        setIsEditing(!isEditing);
                    }}
                    color={isEditing ? 'red' : 'green'}
                />
            </View>

            <Button
                title={isSendingData ? 'Stop Sending Data' : 'Start Sending Data'}
                onPress={toggleDataSending}
                color={isSendingData ? 'red' : 'green'}
            />

            <View style={styles.sensorDataContainer}>
                <Text style={styles.sensorDataTitle}>Sensor Data:</Text>
                <Text>Accel: X={sensorData.accelX.toFixed(2)} Y={sensorData.accelY.toFixed(2)} Z={sensorData.accelZ.toFixed(2)}</Text>
                <Text>Gyro: X={sensorData.gyroX.toFixed(2)} Y={sensorData.gyroY.toFixed(2)} Z={sensorData.gyroZ.toFixed(2)}</Text>
                <Text>Location: Lat={sensorData.latitude.toFixed(5)} Long={sensorData.longitude.toFixed(5)}</Text>
                <Text>Speed: {sensorData.speed.toFixed(2)} m/s</Text>
            </View>

            {showBedsInput ? (
                <View style={styles.accidentContainer}>
                    <Text style={styles.accidentText}>Accident detected nearby!</Text>
                    <TextInput
                        style={styles.input}
                        placeholder="Number of beds available"
                        value={bedsNumber}
                        onChangeText={setBedsNumber}
                        keyboardType="numeric"
                    />
                    <Button title="Send Beds Data" onPress={sendBedsData} color="blue" />
                </View>
            ) : (
                <Text style={styles.noAccidentText}>No accidents detected nearby</Text>
            )}
        </View>
    );
};

const styles = StyleSheet.create({
    container: {
        flex: 1,
        padding: 20,
        backgroundColor: '#f5f5f5',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20,
        textAlign: 'center',
    },
    inputContainer: {
        flexDirection: 'row',
        alignItems: 'center',
        marginBottom: 15,
    },
    input: {
        flex: 1,
        borderWidth: 1,
        borderColor: '#ccc',
        borderRadius: 5,
        padding: 10,
        marginRight: 10,
    },
    sensorDataContainer: {
        marginTop: 20,
        padding: 15,
        backgroundColor: '#fff',
        borderRadius: 5,
        borderWidth: 1,
        borderColor: '#ddd',
    },
    sensorDataTitle: {
        fontWeight: 'bold',
        marginBottom: 10,
    },
    accidentContainer: {
        marginTop: 20,
        padding: 15,
        backgroundColor: '#ffebee',
        borderRadius: 5,
        borderWidth: 1,
        borderColor: '#ef9a9a',
    },
    accidentText: {
        color: 'red',
        fontWeight: 'bold',
        marginBottom: 10,
    },
    noAccidentText: {
        marginTop: 20,
        color: 'green',
        textAlign: 'center',
    },
});

export default App;
