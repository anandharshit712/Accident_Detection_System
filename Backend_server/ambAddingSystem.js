const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');
const Alert = require('./models/alert');
const AmbAlert = require('./models/ambAlert');
const HospitalStatus = require('./models/hospitalStatus');

const ambulanceSchema = new mongoose.Schema({
  hospitalID: Number,
  ambulanceId: [{ ID: Number, status: Boolean }],
});
const AmbulanceList = mongoose.model("ambulancelist", ambulanceSchema);

// Endpoint to add ambulance data
router.post("/add-ambulance", async (req, res) => {
  try {
    const newAmbulance = new AmbulanceList(req.body);
    await newAmbulance.save();
    res.status(201).send("Ambulance data added");
  } catch (err) {
    res.status(400).send(err);
  }
});

// Endpoint to get all ambulance data
router.get("/get-ambulance", async (req, res) => {
  try {
    const data = await AmbulanceList.find();
    res.status(200).json(data);
  } catch (err) {
    res.status(500).send(err);
  }
});

router.put("/set-ambulance-true/:id", async (req, res) => {
  const ambulanceID = parseInt(req.params.id);

  try {
    const result = await AmbulanceList.findOneAndUpdate(
      { "ambulanceId.ID": ambulanceID },
      { $set: { "ambulanceId.$.status": true } },
      { new: true }
    );

    if (!result) {
      return res.status(404).send("Ambulance ID not found");
    }

    res.status(200).json(result);
  } catch (err) {
    res.status(500).send(err);
  }
});

// Endpoint to set ambulance status to false by ID
router.put("/set-ambulance-false/:id", async (req, res) => {
  const ambulanceID = parseInt(req.params.id);

  try {
    const result = await AmbulanceList.findOneAndUpdate(
      { "ambulanceId.ID": ambulanceID },
      { $set: { "ambulanceId.$.status": false } },
      { new: true }
    );

    if (!result) {
      return res.status(404).send("Ambulance ID not found");
    }

    res.status(200).json(result);
  } catch (err) {
    res.status(500).send(err);
  }
});

// Function to monitor alert collection every second
setInterval(async () => {
  try {
    const alerts = await Alert.find({ status: true });
    //console.log(alerts);
    for (const alert of alerts) {
      const { hospitalID, latitude, longitude, noOfBeds } = alert;

      const newhalert = new HospitalStatus({
        hID: hospitalID,
        lat: latitude,
        long: longitude,
        status: true,
        nofBeds: noOfBeds,
      })
      await newhalert.save();

      const ambulanceData = await AmbulanceList.findOne({ hospitalID });
      //console.log(ambulanceData);
      if (ambulanceData) {
        const availableAmbulances = ambulanceData.ambulanceId.filter(a => a.status === true).slice(0, noOfBeds);
        //console.log(availableAmbulances);
        for (const ambulance of availableAmbulances) {
          const newAmbAlert = new AmbAlert({
            ambulanceId: ambulance.ID,
            status: true,
            latitude,
            longitude,
          });
          //console.log(newAmbAlert);
          await newAmbAlert.save();
        }
        // Set alert status to false after processing
        await Alert.updateOne({ _id: alert._id }, { $set: { status: false } });
      }
    }
  } catch (error) {
    console.error("Error in alert monitoring:", error);
  }
}, 1000);

module.exports = router;