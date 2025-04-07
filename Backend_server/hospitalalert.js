const express = require('express');
const router = express.Router()
const mongoose = require('mongoose');
const HospitalStatus= require('./models/hospitalStatus');

// Endpoint to insert data
router.post('/api/hospital-status', async (req, res) => {
    try {
      const newEntry = new HospitalStatus(req.body);
      await newEntry.save();
      res.status(201).json({ message: 'Data saved successfully' });
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
  
  // Endpoint to check for active status of specific hospital
  router.get('/api/hospstatus/:hID', async (req, res) => {
    try {
      const { hID } = req.params;
      const activeStatus = await HospitalStatus.findOne({
        hID,
        status: true,
      }).sort({ timestamp: -1 });
      
      if (activeStatus) {
        res.json(activeStatus);
      } else {
        res.status(404).json({ message: 'No active status found' });
      }
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });
  
  // Endpoint to get full log of a hospital
  router.get('/api/hospital-log/:hID', async (req, res) => {
    try {
      const { hID } = req.params;
      const logs = await HospitalStatus.find({ hID }).sort({ timestamp: -1 });
      res.json(logs);
    } catch (error) {
      res.status(500).json({ error: error.message });
    }
  });




module.exports = router;