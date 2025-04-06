const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');
const huserModel= require('./models/huserModel');

// Login endpoint
router.post('/hosp-login', async (req, res) => {
  const { h_ID, password } = req.body;
  const user = await huserModel.findOne({ h_ID, password });
  if (user) {
    res.json({ success: true });
  } else {
    res.json({ success: false });
  }
});


// Register a new ambulance
router.post('/hosp-register', async (req, res) => {
  const { h_ID, password } = req.body;
  const existingAmbulance = await huserModel.findOne({ h_ID });
  if (existingAmbulance) {
    return res.status(400).json({ success: false, message: 'Hospital already exists' });
  }
  const newHospital = new huserModel({ h_ID, password });
  await newHospital.save();
  res.json({ success: true, message: 'Hospital registered successfully' });
});

module.exports = router;