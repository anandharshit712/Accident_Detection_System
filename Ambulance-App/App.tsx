import React, { useEffect, useState } from 'react';
import { View, Text, Button, TextInput, Alert,StyleSheet,Image,TouchableOpacity } from 'react-native';
import AsyncStorage from '@react-native-async-storage/async-storage';
import notifee, { AndroidImportance } from '@notifee/react-native';
import { openURL } from 'react-native-linking';
import axios from 'axios';
import BackgroundTimer from 'react-native-background-timer';

import logo from './logo.png';
import gf from './amb.gif';

const API_URL = 'https://crash-api-six.vercel.app'; // Replace with your actual Express API URL

const setStatus = async (id, toTrue) => {
  try {
    const route = toTrue ? 'set-ambulance-true' : 'set-ambulance-false';
    const response = await fetch(`${API_URL}/${route}/${id}`, {
      method: 'PUT',
    });

    const data = await response.json();
    if (response.ok) {
      Alert.alert('Success', `Status updated for ID ${id}`);
    } else {
      Alert.alert('Error', data.message || 'Failed to update status');
    }
  } catch (error) {
    console.error(error);
    Alert.alert('Network Error', 'Could not connect to server');
  }
};

const LoginScreen = ({ onLogin }) => {
  const [ambulanceId, setAmbulanceId] = useState('');
  const [password, setPassword] = useState('');

  const handleLogin = async () => {
    try {
      const response = await axios.post(`${API_URL}/anb_login`, { ambulanceId, password });
      if (response.data.success) {
        await AsyncStorage.setItem('ambulanceId', ambulanceId);
        onLogin(ambulanceId);
      } else {
        Alert.alert('Login Failed', 'Invalid ID or Password');
      }
    } catch (error) {
      Alert.alert('Login Error', 'Could not connect to server');
    }
  };

  return (
    <View style={styles.container}>
      <Image source={logo} style={styles.logo} />
      <Text style={styles.title}>Login</Text>
      <View style={styles.inputContainer}>
      <TextInput style={styles.input} placeholder="Ambulance ID" onChangeText={setAmbulanceId} value={ambulanceId} />
      </View>
      <View style={styles.inputContainer}>
      <TextInput style={styles.input} placeholder="Password" secureTextEntry onChangeText={setPassword} value={password} />
      </View>
      {/* <Button title="Login" onPress={handleLogin} /> */}
      <TouchableOpacity
              style={styles.button}
              onPress={handleLogin}
              
            >
              <Text style={styles.buttonText}>Login</Text>
            </TouchableOpacity>
    </View>
  );
};

const MonitoringScreen = ({ ambulanceId, onLogout }) => {
  const [location, setLocation] = useState(null);

  useEffect(() => {
    checkDatabase();
    BackgroundTimer.runBackgroundTimer(() => {
      checkDatabase();
    }, 60000); // Run every 1 minute

    return () => BackgroundTimer.stopBackgroundTimer(); // Cleanup on unmount
  }, []);

  const checkDatabase = async () => {
    try {
      const response = await axios.get(`${API_URL}/ambdata/${ambulanceId}`);
      const data = response.data;
      const activeEntry = data.find(entry => entry.status === true);
      
      if (activeEntry) {
        setLocation(activeEntry);
        triggerNotification(activeEntry.latitude, activeEntry.longitude);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
    }
  };

  const triggerNotification = async (lat, lng) => {
    await notifee.requestPermission();
    const channelId = await notifee.createChannel({
      id: 'emergency-alert',
      name: 'Emergency Alerts',
      importance: AndroidImportance.HIGH,
      sound: 'default',
    });

    await notifee.displayNotification({
      title: 'Emergency Alert!',
      body: `Location detected: Lat ${lat}, Lng ${lng}`,
      android: {
        channelId,
        sound: 'default',
        pressAction: { id: 'default' },
      },
    });
  };

  const openGoogleMaps = async (lat, lng) => {
    setStatus(ambulanceId, false);
    const url = `https://www.google.com/maps/dir/?api=1&destination=${lat},${lng}`;
    await axios.put(`${API_URL}/ambupdate-status/${ambulanceId}`); // Update status to false
    openURL(url).catch(err => console.error('Failed to open Google Maps:', err));
  };

  const handleLogout = async () => {
    await AsyncStorage.removeItem('ambulanceId');
    onLogout();
  };

  return (
    <View style={styles.container}>
      <Image source={gf} style={styles.gf} />
      
      <Text >Waiting for Alerts...</Text>
      {location && (
        <TouchableOpacity
        style={styles.button3}
        onPress={() => openGoogleMaps(location.latitude, location.longitude)}
        
      >
        <Text style={styles.buttonText}>Open Google Maps</Text>
      </TouchableOpacity>
        // <Button title="Open Google Maps" onPress={() => openGoogleMaps(location.latitude, location.longitude)} />
      )}
    
            
      {/* <Button  title="Logout" onPress={handleLogout} /> */}
      <TouchableOpacity
              style={styles.button2}
              onPress={handleLogout}
              
            >
              <Text style={styles.buttonText}>LOGOUT</Text>
            </TouchableOpacity>

      {/* <Button title="Ready" onPress={() => setStatus(ambulanceId, true)} /> */}
      <View style={{ height: 10 }} />
      <TouchableOpacity style={styles.button2} onPress={() => setStatus(ambulanceId, true)}>
              <Text style={styles.buttonText}>Ready</Text>
      </TouchableOpacity>
      {/* <Button title="Set Ambulance 1 Status to FALSE" onPress={() => setStatus(ambulanceId, false)} /> */}
    </View>
  );
};

const App = () => {
  const [ambulanceId, setAmbulanceId] = useState(null);

  useEffect(() => {
    const loadAmbulanceId = async () => {
      const storedId = await AsyncStorage.getItem('ambulanceId');
      if (storedId) {
        setAmbulanceId(storedId);
      }
    };
    loadAmbulanceId();
  }, []);

  return ambulanceId ? (
    <MonitoringScreen ambulanceId={ambulanceId} onLogout={() => setAmbulanceId(null)} />
  ) : (
    <LoginScreen onLogin={setAmbulanceId} />
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    justifyContent: 'center',
    alignItems: 'center',
    backgroundColor: '#fff',
    
    paddingHorizontal: 20,
  },
  logo: {
    height: 200,
    width: 200,
    resizeMode: 'contain',
    marginBottom: 20,
  },
  gf: {
    height: 150,
    width: 200,
    resizeMode: 'contain',
    margin: 0,
  },
  title: {
    fontSize: 32,
    marginBottom: 40,
    fontWeight: 'bold',
    color: 'black',
  },
  inputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    width: '100%',
    height: 50,
    backgroundColor: '#f1f1f1',
    borderRadius: 8,
    paddingHorizontal: 10,
    marginBottom: 20,
  },
  but: {
    
    width: '100%',
    height: 50,
    borderRadius: 8,
    paddingHorizontal: 10,
    marginTop: 20,
  },
  button: {
    width: '100%',
    height: 50,
    backgroundColor: '#1E90FF',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 20,
  },
  button3: {
    width: '60%',
    height: 50,
    backgroundColor: '#1E90FF',
    borderRadius: 8,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  button2: {
    width: '30%',
    height: 40,
    backgroundColor: '#ff0000',
    borderRadius: 10,
    justifyContent: 'center',
    alignItems: 'center',
    marginTop: 20,
  },
  buttonText: {
    color: '#fff',
    fontSize: 18,
  },
  
  
});

export default App;
