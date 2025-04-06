require('dotenv').config()
const express = require("express");
const mongoose = require("mongoose");
const bodyParser = require("body-parser");
const cors = require("cors");

const app = express();
app.use(bodyParser.json());
// Middleware
app.use(cors());
app.use(express.json());

// Connect to MongoDB Atlas
const dbURI = 'mongodb+srv://satya288:hellomini@spnweb.2nt6szt.mongodb.net/?retryWrites=true&w=majority&appName=spnweb';
mongoose.connect(dbURI, { useNewUrlParser: true, useUnifiedTopology: true })
    .then(() => console.log("Connected to MongoDB Atlas"))
    .catch(err => console.log("Error: ", err));
//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// Routes
app.use('/',require("./hospitalPage"));
app.use('/',require("./forHospitalPage"));
app.use('/',require("./ambulance_app"));
app.use('/',require("./ambAddingSystem"));
app.use('/',require("./hlogin"));
app.use('/',require("./hospitalalert"));
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

const sensorDataSchema = new mongoose.Schema({
    ID: { type: String, required: true }, // Make mobile number required
    latitude: Number,
    longitude: Number,
    speed: Number,
    accelX: Number,
    accelY: Number,
    accelZ: Number,
    gyroX: Number,
    gyroY: Number,
    gyroZ: Number,
    timestamp: { type: Date, default: Date.now } // Add a timestamp for each entry
  });
  
  const SensorData = mongoose.model("SensorData", sensorDataSchema);

  // Beds Schema and Model
const bedsSchema = new mongoose.Schema({
  lat: Number,
  long: Number,
  ID: { type: Number, unique: true },
  status: Boolean,
  no_of_beds: [Number],
});
const Beds = mongoose.model("Beds", bedsSchema);

// Accident Schema and Model
const accidentSchema = new mongoose.Schema({
  lat: Number,
  long: Number,
  ID: Number,
  status: Boolean,
});
const Accident = mongoose.model("Accident", accidentSchema);
  
  // Endpoint to handle sensor data upload
  app.post("/upload_sensor_data", async (req, res) => {
    console.log("Received data:", req.body); // Log received data
    const { ID, latitude, longitude, speed, accelX, accelY, accelZ, gyroX, gyroY, gyroZ } = req.body;
  
    try {
      // Create a new document for each data point
      const newSensorData = new SensorData({
        ID,
        latitude,
        longitude,
        speed,
        accelX,
        accelY,
        accelZ,
        gyroX,
        gyroY,
        gyroZ,
      });
  
      await newSensorData.save();
      res.status(201).send("Data saved successfully"); // Use status code 201 for created resources
    } catch (error) {
      res.status(500).send("Error saving data");
      console.error("Database Error:", error);
    }
  });

  //////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

  async function deleteOldData() {
    const threshold = Date.now() - 5000; // Current time minus 5 seconds
    try {
      await SensorData.deleteMany({ timestamp: { $lt: threshold } });
      //console.log("Old data deleted successfully!");
    } catch (error) {
      console.error("Error deleting old data:", error);
    }
  }
  
  // Start the interval to delete old data every second
  setInterval(deleteOldData, 1000); // 1000 milliseconds = 1 second

  ///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
  // 2. Endpoint to check accident clusters
app.get('/check_accidents', async (req, res) => {
  try {
      const clusters = await AccidentCluster.find({ accidentStatus: true });
      res.status(200).json({ accidents: clusters });
  } catch (error) {
      console.error("Error fetching accident clusters:", error);
      res.status(500).json({ message: "Failed to fetch accident clusters", error });
  }
});

////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
app.get("/accident-status", async (req, res) => {
  try {
    const activeAccident = await Accident.findOne({ status: true });

    if (activeAccident) {
      // Send the response first
      res.status(200).json(activeAccident);

      // Delay the status update
      setTimeout(async () => {
        await Accident.updateOne({ _id: activeAccident._id }, { $set: { status: false } })
          .catch(err => {
            console.error("Error updating accident status:", err);
          });
      }, 9669); // 4 seconds delay
    } else {
      res.status(404).json({ message: "No active accidents found" });
    }
  } catch (error) {
    res.status(500).json({ error: "Error fetching accident status" });
  }
});

// Endpoint to post data to beds cluster
app.post("/beds", async (req, res) => {
  try {
      const { lat, long, ID, status, no_of_beds } = req.body;

      const existingBeds = await Beds.findOne({ ID });

      if (existingBeds) {
          existingBeds.no_of_beds.push(...no_of_beds);
          existingBeds.status = status;
          await existingBeds.save();
          return res.status(200).json({ message: "Beds updated successfully" });
      } else {
          const newBeds = new Beds({ lat, long, ID, status, no_of_beds });
          await newBeds.save();
          return res.status(201).json({ message: "Beds data added successfully" });
      }
  } catch (error) {
      res.status(500).json({ error: "Error saving beds data" });
  }
});

// Endpoint to post data to Accident collection
app.post("/accidents", async (req, res) => {
  const { lat, long, ID, status } = req.body;
  console.log(req.body)

  try {
    const newRecord = new Accident({ lat, long, ID, status });
    await newRecord.save();
    res.status(201).json({ message: "Accident data added successfully", data: newRecord });
  } catch (error) {
    res.status(500).json({ message: "Error adding Accident data", error: error.message });
  }
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////

const port = process.env.PORT || 9000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});