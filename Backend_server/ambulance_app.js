const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');
const Alert= require('./models/alert');
const ambAlert= require('./models/ambAlert');

const ambulanceSchema = new mongoose.Schema({
  ambulanceId: Number,
  password: String,
});

const Ambulance = mongoose.model('Ambulance', ambulanceSchema);


// Login endpoint
router.post('/anb_login', async (req, res) => {
  const { ambulanceId, password } = req.body;
  const user = await Ambulance.findOne({ ambulanceId, password });
  if (user) {
    res.json({ success: true });
  } else {
    res.json({ success: false });
  }
});

// Fetch active alert for specific ambulance
router.get('/ambdata/:ambulanceId', async (req, res) => {
  const { ambulanceId } = req.params;
  const data = await ambAlert.find({ ambulanceId });
  res.json(data);
});

// Push new alert data
router.post('/ambdata', async (req, res) => {
  const { ambulanceId, status, latitude, longitude } = req.body;
  const newAlert = new ambAlert({ ambulanceId, status, latitude, longitude });
  await newAlert.save();
  res.json({ success: true });
});

// Update alert status to false when Google Maps is opened
router.put('/ambupdate-status/:ambulanceId', async (req, res) => {
  const { ambulanceId } = req.params;
  await ambAlert.updateMany({ ambulanceId, status: true }, { status: false });
  res.json({ success: true, message: 'Status updated to false' });
});

// Fetch all ambulances
router.get('/ambambulances', async (req, res) => {
  const ambulances = await Ambulance.find();
  res.json(ambulances);
});

// Register a new ambulance
router.post('/ambregister', async (req, res) => {
  const { ambulanceId, password } = req.body;
  const existingAmbulance = await Ambulance.findOne({ ambulanceId });
  if (existingAmbulance) {
    return res.status(400).json({ success: false, message: 'Ambulance ID already exists' });
  }
  const newAmbulance = new Ambulance({ ambulanceId, password });
  await newAmbulance.save();
  res.json({ success: true, message: 'Ambulance registered successfully' });
});

module.exports = router;