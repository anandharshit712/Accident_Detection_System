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
////////////////////////////////////////////////////////////////////////////////

// Define data schema and model aviskhit
const alertSchema = new mongoose.Schema({
  mobileNumber: { type: String, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  status: { type: Boolean, required: true },
  timestamp: { type: Date, default: Date.now },
  noOfBeds: { type: Number, required: true },
});

const Data = mongoose.model("alert", alertSchema);


// Endpoint to post data aviskhit
app.post("/postData", async (req, res) => {
  try {
      const { mobileNumber, latitude, longitude, status, noOfBeds } = req.body;
      const newData = new Data({ mobileNumber, latitude, longitude, status, noOfBeds });
      await newData.save();
      res.status(201).json({ message: "Data saved successfully!" });
  } catch (error) {
      console.error("Error saving data:", error);
      res.status(500).json({ error: "Failed to save data" });
  }
});

// Endpoint to check if any data has status === true aviskhit
app.get("/checkStatus", async (req, res) => {
  try {
    const result = await Data.findOne({ status: true }).select(
      "mobileNumber latitude longitude noOfBeds timestamp"
    );

    if (result) {
      // Update the status to false after fetching the data
      await Data.updateOne({ _id: result._id }, { $set: { status: false } });

      res.status(200).json(result);
    } else {
      res.status(200).json(null); // No matching records
    }
  } catch (error) {
    console.error("Error checking status:", error);
    res.status(500).json({ error: "Failed to check status" });
  }
});

// Endpoint to update status aviskhit
app.post("/updateStatus", async (req, res) => {
  try {
      const { _id } = req.body;
      await Data.findByIdAndUpdate(_id, { status: false });
      res.status(200).json({ message: "Status updated successfully!" });
  } catch (error) {
      console.error("Error updating status:", error);
      res.status(500).json({ error: "Failed to update status" });
  }
});

// Endpoint to fetch all data avikshit
app.get("/getAllData", async (req, res) => {
  try {
      const allData = await Data.find();
      res.status(200).json(allData);
  } catch (error) {
      console.error("Error fetching data:", error);
      res.status(500).json({ error: "Failed to fetch data" });
  }
});
    ////////////////////////////////////////////////////////////////////////////////////////////

const sensorDataSchema = new mongoose.Schema({
    mobileNumber: { type: String, required: true }, // Make mobile number required
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

  // Beds Schema and Model_backend
const bedsSchema = new mongoose.Schema({
  lat: Number,
  long: Number,
  mobile_number: { type: Number, unique: true },
  status: Boolean,
  no_of_beds: [Number],
});
const Beds = mongoose.model("Beds", bedsSchema);

// Accident Schema and Model_backend
const accidentSchema = new mongoose.Schema({
  lat: Number,
  long: Number,
  mobile_number: Number,
  status: Boolean,
});
const Accident = mongoose.model("Accident", accidentSchema);

  // Endpoint to handle sensor data upload
  app.post("/upload_sensor_data", async (req, res) => {
    console.log("Received data:", req.body); // Log received data
    const { mobileNumber, latitude, longitude, speed, accelX, accelY, accelZ, gyroX, gyroY, gyroZ } = req.body;

    try {
      // Create a new document for each data point
      const newSensorData = new SensorData({
        mobileNumber,
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

// Endpoint to check for accident status
// app.get("/accident-status", async (req, res) => {
//   try {
//       const activeAccident = await Accident.findOne({ status: true });
//       if (activeAccident) {
//           res.status(200).json(activeAccident);
//       } else {
//           res.status(404).json({ message: "No active accidents found" });
//       }
//   } catch (error) {
//       res.status(500).json({ error: "Error fetching accident status" });
//   }
// });
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
      const { lat, long, mobile_number, status, no_of_beds } = req.body;

      const existingBeds = await Beds.findOne({ mobile_number });

      if (existingBeds) {
          existingBeds.no_of_beds.push(...no_of_beds);
          existingBeds.status = status;
          await existingBeds.save();
          return res.status(200).json({ message: "Beds updated successfully" });
      } else {
          const newBeds = new Beds({ lat, long, mobile_number, status, no_of_beds });
          await newBeds.save();
          return res.status(201).json({ message: "Beds data added successfully" });
      }
  } catch (error) {
      res.status(500).json({ error: "Error saving beds data" });
  }
});

// Endpoint to post data to Accident collection
app.post("/accidents", async (req, res) => {
  const { lat, long, mobile_number, status } = req.body;
  console.log(req.body)

  try {
    const newRecord = new Accident({ lat, long, mobile_number, status });
    await newRecord.save();
    res.status(201).json({ message: "Accident data added successfully", data: newRecord });
  } catch (error) {
    res.status(500).json({ message: "Error adding Accident data", error: error.message });
  }
});

//////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

// Hospital Schema and Model_backend
const hospitalSchema = new mongoose.Schema({
  hospitalID: { type: Number, unique: true, required: true },
  latitude: { type: Number, required: true },
  longitude: { type: Number, required: true },
  total_of_available_beds: { type: Number, required: true },
  no_of_available_beds: { type: Number, required: true }
});

const Hospital = mongoose.model('Hospital', hospitalSchema);

// Routes

// Create and Add Hospital Data
app.post('/hospital', async (req, res) => {
  try {
    const hospital = new Hospital(req.body);
    await hospital.save();
    res.status(201).json(hospital);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Find Hospital by hospitalID
app.get('/hospital/:id', async (req, res) => {
  try {
    const hospital = await Hospital.findOne({ hospitalID: req.params.id });
    if (!hospital) {
      return res.status(404).json({ message: "Hospital not found" });
    }
    res.json(hospital);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});

// Update no_of_available_beds by hospitalID
app.patch('/hospital/:id', async (req, res) => {
  try {
    const { no_of_available_beds } = req.body;
    const hospital = await Hospital.findOneAndUpdate(
      { hospitalID: req.params.id },
      { $set: { no_of_available_beds } },
      { new: true }
    );
    if (!hospital) {
      return res.status(404).json({ message: "Hospital not found" });
    }
    res.json(hospital);
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
});



const port = process.env.PORT || 9000;
app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});
