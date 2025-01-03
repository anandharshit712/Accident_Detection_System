package com.example.bkltracker;

import android.Manifest;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.hardware.Sensor;
import android.hardware.SensorEvent;
import android.hardware.SensorEventListener;
import android.hardware.SensorManager;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Bundle;
import android.os.Handler;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.TextView;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.os.Build;
import android.widget.Toast;

import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.app.NotificationManagerCompat;
import androidx.core.content.ContextCompat;
import androidx.core.app.NotificationCompat;

import com.google.gson.Gson;
import com.google.gson.reflect.TypeToken;

import org.jetbrains.annotations.NotNull;

import java.io.IOException;
import java.util.HashMap;

import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;

import org.json.JSONObject;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Objects;

public class MainActivity extends AppCompatActivity implements SensorEventListener, LocationListener {

    private EditText mobileNumberEditText;
    private TextView sensorDataTextView;
    private Button toggleButton, editSaveButton;

    private SensorManager sensorManager;
    private LocationManager locationManager;
    private boolean isSendingData = false;

    private float accelX, accelY, accelZ;
    private float gyroX, gyroY, gyroZ;
    private double latitude, longitude, speed;

    private String mobileNumber;
    private Handler handler;
    //private Handler handler = new Handler();
    private Runnable dataSender;

    private SharedPreferences sharedPreferences;

    private static final String BEDS_CLUSTER_URL = "https://accident-cisl.onrender.com/beds";
    private static final String CHANNEL_ID = "accident_notifications";
    private static final int REQUEST_CODE_POST_NOTIFICATIONS = 1;

    private TextView notificationText;
    private EditText inputNumber;
    private Button sendButton;

    private OkHttpClient client;

    private HashMap<String, Object> currentAccidentData; // To store active accident data

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);

        mobileNumberEditText = findViewById(R.id.mobileNumberEditText);
        sensorDataTextView = findViewById(R.id.sensorDataTextView);
        toggleButton = findViewById(R.id.toggleButton);
        editSaveButton = findViewById(R.id.editSaveButton);

        sensorManager = (SensorManager) getSystemService(Context.SENSOR_SERVICE);
        locationManager = (LocationManager) getSystemService(Context.LOCATION_SERVICE);

        sharedPreferences = getSharedPreferences("UserData", MODE_PRIVATE);
        mobileNumber = sharedPreferences.getString("mobileNumber", "");
        mobileNumberEditText.setText(mobileNumber);
        mobileNumberEditText.setEnabled(false);

        if (ActivityCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.ACCESS_FINE_LOCATION}, 1);
        } else {
            locationManager.requestLocationUpdates(LocationManager.GPS_PROVIDER, 1000, 0, this);
        }

        registerSensors();

        toggleButton.setOnClickListener(v -> toggleDataSending());
        editSaveButton.setOnClickListener(v -> toggleEditSaveNumber());

        // Initialize views
        notificationText = findViewById(R.id.notificationText);
        inputNumber = findViewById(R.id.inputNumber);
        sendButton = findViewById(R.id.sendButton);
        handler = new Handler();
        client = new OkHttpClient();

        // Check and request POST_NOTIFICATIONS permission
        checkNotificationPermission();

        // Create notification channel
        createNotificationChannel();

        // Poll for accident data every 2 seconds
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                fetchAccidentData();
                handler.postDelayed(this, 2000); // Repeat every 2 seconds
            }
        }, 2000);

        // Handle Send button click
        sendButton.setOnClickListener(v -> sendBedsData());
    }

    private void registerSensors() {
        sensorManager.registerListener(this, sensorManager.getDefaultSensor(Sensor.TYPE_ACCELEROMETER), SensorManager.SENSOR_DELAY_NORMAL);
        sensorManager.registerListener(this, sensorManager.getDefaultSensor(Sensor.TYPE_GYROSCOPE), SensorManager.SENSOR_DELAY_NORMAL);
    }

    private void toggleDataSending() {
        if (isSendingData) {
            stopSendingData();
            toggleButton.setText("Start Sending Data");
            toggleButton.setBackgroundColor(Color.GREEN);
        } else {
            mobileNumber = mobileNumberEditText.getText().toString();
            if (!mobileNumber.isEmpty()) {
                startSendingData();
                toggleButton.setText("Stop Sending Data");
                toggleButton.setBackgroundColor(Color.RED);
            }
        }
    }

    private void toggleEditSaveNumber() {
        if (mobileNumberEditText.isEnabled()) {
            // Save the edited number
            mobileNumberEditText.setEnabled(false);
            SharedPreferences.Editor editor = sharedPreferences.edit();
            editor.putString("mobileNumber", mobileNumberEditText.getText().toString());
            editor.apply();
            editSaveButton.setText("Edit");
            editSaveButton.setBackgroundColor(Color.GREEN);
        } else {
            // Enable editing
            mobileNumberEditText.setEnabled(true);
            editSaveButton.setText("Save");
            editSaveButton.setBackgroundColor(Color.RED);
        }
    }

    private void startSendingData() {
        isSendingData = true;
        dataSender = new Runnable() {
            @Override
            public void run() {
                sendDataToServer();
                handler.postDelayed(this, 1000);
            }
        };
        handler.post(dataSender);
    }

    private void stopSendingData() {
        isSendingData = false;
        handler.removeCallbacks(dataSender);
    }


    private void sendDataToServer() {
        new Thread(() -> {
            try {
                // Constructing JSON data
                JSONObject jsonObject = new JSONObject();
                jsonObject.put("mobileNumber", mobileNumber);
                jsonObject.put("latitude", latitude);
                jsonObject.put("longitude", longitude);
                jsonObject.put("speed", speed);
                jsonObject.put("accelX", accelX);
                jsonObject.put("accelY", accelY);
                jsonObject.put("accelZ", accelZ);
                jsonObject.put("gyroX", gyroX);
                jsonObject.put("gyroY", gyroY);
                jsonObject.put("gyroZ", gyroZ);

//                JSONObject jsonObject = new JSONObject();
//                jsonObject.put("mobileNumber", 696969696);
//                jsonObject.put("latitude", 2.450355);
//                jsonObject.put("longitude", -76.6264806);
//                jsonObject.put("speed", 4.50036);
//                jsonObject.put("accelX", 0.2246864);
//                jsonObject.put("accelY", 1.1108867);
//                jsonObject.put("accelZ", 9.9796008);
//                jsonObject.put("gyroX", -4.042993);
//                jsonObject.put("gyroY", 1.1893435);
//                jsonObject.put("gyroZ", -19.9595413);

                Log.d("DataTransmission", "Sending JSON: " + jsonObject.toString()); // Log the data here

                URL url = new URL("https://accident-cisl.onrender.com/upload_sensor_data");
                HttpURLConnection conn = (HttpURLConnection) url.openConnection();
                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "application/json");

                OutputStream os = conn.getOutputStream();
                byte[] input = jsonObject.toString().getBytes("utf-8");
                os.write(input, 0, input.length);

                if (conn.getResponseCode() == HttpURLConnection.HTTP_OK) {
                    Log.d("DataTransmission", "Data sent successfully");
                }

                conn.disconnect();
            } catch (Exception e) {
                e.printStackTrace();
            }
        }).start();
    }

    private void checkNotificationPermission() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this,
                        new String[]{Manifest.permission.POST_NOTIFICATIONS},
                        REQUEST_CODE_POST_NOTIFICATIONS);
            }
        }
    }

    private double calculateDistance(double lat1, double lon1, double lat2, double lon2) {
//        double latDiff = lat2 - lat1;
//        double lonDiff = lon2 - lon1;
//
//        return Math.sqrt(latDiff * latDiff + lonDiff * lonDiff) * 111139; // Approx. conversion to meters
        return 400.00;
    }

    private void fetchAccidentData() {
        Request request = new Request.Builder()
                .url("https://accident-cisl.onrender.com/accident-status") // Use the new endpoint
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.e("AccidentData", "Error fetching accident status", e);
            }

            //            @Override
//            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
//                if (response.isSuccessful()) {
//                    String responseBody = response.body().string();
//                    Log.d("AccidentData", responseBody);
//
//                    Gson gson = new Gson();
//                    HashMap<String, Object> accident = gson.fromJson(responseBody, new TypeToken<HashMap<String, Object>>() {}.getType());
//
//                    // Only process if accident status is true
//                    if (accident != null) {
//                        currentAccidentData = accident;
//                        showAccidentNotification();
//                    }
//
//                } else if (response.code() == 404) {
//                    Log.d("AccidentData", "No active accidents");
//                }
//            }
            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) throws IOException {
                if (response.isSuccessful()) {
                    String responseBody = response.body().string();
                    currentAccidentData = new Gson().fromJson(responseBody, new TypeToken<HashMap<String, Object>>() {
                    }.getType());

                    if (currentAccidentData != null) {
                        double accidentLat = (double) currentAccidentData.get("lat");
                        double accidentLong = (double) currentAccidentData.get("long");


                        double distance = calculateDistance(latitude, longitude, accidentLat, accidentLong);

                        if (distance <= 500) {
                            showAccidentNotification();
                        }
                    }
                }
            }

        });
    }


    //    private void showAccidentNotification() {
//        runOnUiThread(() -> {
//            notificationText.setText("Accident detected nearby!");
//            inputNumber.setVisibility(View.VISIBLE);
//            sendButton.setVisibility(View.VISIBLE);
//
//            NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
//                    .setSmallIcon(android.R.drawable.ic_dialog_alert)
//                    .setContentTitle("Accident Alert")
//                    .setContentText("An accident has been detected nearby!")
//                    .setPriority(NotificationCompat.PRIORITY_HIGH);
//
//            NotificationManager manager = (NotificationManager) getSystemService(Context.NOTIFICATION_SERVICE);
//            manager.notify(1, builder.build());
//        });
//    }
    private void showAccidentNotification() {
        runOnUiThread(() -> {
            notificationText.setText("Accident detected nearby!");
            inputNumber.setVisibility(View.VISIBLE);
            sendButton.setVisibility(View.VISIBLE);

            NotificationCompat.Builder builder = new NotificationCompat.Builder(this, CHANNEL_ID)
                    .setSmallIcon(android.R.drawable.ic_dialog_alert)
                    .setContentTitle("Accident Alert")
                    .setContentText("An accident has been detected within 100 meters!")
                    .setPriority(NotificationCompat.PRIORITY_HIGH);

            NotificationManagerCompat manager = NotificationManagerCompat.from(this);
            if (ActivityCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                // TODO: Consider calling
                //    ActivityCompat#requestPermissions
                // here to request the missing permissions, and then overriding
                //   public void onRequestPermissionsResult(int requestCode, String[] permissions,
                //                                          int[] grantResults)
                // to handle the case where the user grants the permission. See the documentation
                // for ActivityCompat#requestPermissions for more details.
                return;
            }
            manager.notify(1, builder.build());
    });
}

    private void sendBedsData() {
        String numberInput = inputNumber.getText().toString();
        if (numberInput.isEmpty() || currentAccidentData == null) {
            Toast.makeText(this, "Enter a valid number of beds", Toast.LENGTH_SHORT).show();
            return;
        }

        int bedsNumber = Integer.parseInt(numberInput);
        currentAccidentData.put("status", true);
        currentAccidentData.put("no_of_beds", new int[]{bedsNumber});

        String jsonBody = new Gson().toJson(currentAccidentData);

        RequestBody body = RequestBody.create(
                jsonBody,
                MediaType.get("application/json")
        );

        Request request = new Request.Builder()
                .url(BEDS_CLUSTER_URL)
                .post(body)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(@NotNull Call call, @NotNull IOException e) {
                Log.e("BedsData", "Error sending beds data", e);
                runOnUiThread(() -> Toast.makeText(MainActivity.this, "Failed to send beds data", Toast.LENGTH_SHORT).show());
            }

            @Override
            public void onResponse(@NotNull Call call, @NotNull Response response) {
                if (response.isSuccessful()) {
                    runOnUiThread(() -> {
                        Toast.makeText(MainActivity.this, "Beds data sent successfully!", Toast.LENGTH_SHORT).show();
                        inputNumber.setVisibility(View.GONE);
                        sendButton.setVisibility(View.GONE);
                        notificationText.setText("No accidents detected nearby");
                    });
                }
            }
        });
    }

    private void createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            NotificationChannel channel = new NotificationChannel(
                    CHANNEL_ID,
                    "Accident Notifications",
                    NotificationManager.IMPORTANCE_HIGH
            );
            NotificationManager manager = getSystemService(NotificationManager.class);
            manager.createNotificationChannel(channel);
        }
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults);

        if (requestCode == REQUEST_CODE_POST_NOTIFICATIONS) {
            if (grantResults.length > 0 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                Toast.makeText(this, "Notification permission granted", Toast.LENGTH_SHORT).show();
            } else {
                Toast.makeText(this, "Notification permission denied", Toast.LENGTH_SHORT).show();
            }
        }
    }




    @Override
    public void onSensorChanged(SensorEvent event) {
        switch (event.sensor.getType()) {
            case Sensor.TYPE_ACCELEROMETER:
                accelX = event.values[0];
                accelY = event.values[1];
                accelZ = event.values[2];
                break;
            case Sensor.TYPE_GYROSCOPE:
                gyroX = event.values[0];
                gyroY = event.values[1];
                gyroZ = event.values[2];
                break;
        }

        sensorDataTextView.setText("Accel:"+"\n"+"X=" + accelX +"\n"+ "Y=" + accelY +"\n"+ "Z=" + accelZ + "\n"
                + "Gyro:"+"\n"+"X=" + gyroX +"\n"+ "Y=" + gyroY +"\n"+ "Z=" + gyroZ + "\n"
                + "Location:"+"\n"+"Lat=" + latitude +"\n"+ "Long=" + longitude + "\n"
                + "Speed: " + speed);
    }

    @Override
    public void onLocationChanged(@NonNull Location location) {
        latitude = location.getLatitude();
        longitude = location.getLongitude();
        speed = location.getSpeed();
    }

    @Override
    public void onAccuracyChanged(Sensor sensor, int accuracy) {}
}