const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');


// Hospital Schema and Model
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
router.post('/hospital', async (req, res) => {
  try {
    const hospital = new Hospital(req.body);
    await hospital.save();
    res.status(201).json(hospital);
  } catch (err) {
    res.status(400).json({ error: err.message });
  }
});

// Find Hospital by hospitalID
router.get('/hospital/:id', async (req, res) => {
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
router.patch('/hospital/:id', async (req, res) => {
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

module.exports = router;