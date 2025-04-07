const express = require('express');
const router = express.Router()
const Data= require('./models/alert');

 
  // Endpoint to post data aviskhit
  router.post("/postData", async (req, res) => {
    try {
        const { hospitalID, latitude, longitude, status, noOfBeds } = req.body;
        const newData = new Data({ hospitalID, latitude, longitude, status, noOfBeds });
        await newData.save();
        res.status(201).json({ message: "Data saved successfully!" });
    } catch (error) {
        console.error("Error saving data:", error);
        res.status(500).json({ error: "Failed to save data" });
    }
  });
  
  // Endpoint to check if any data has status === true avikshith
  router.get("/checkStatus", async (req, res) => {
    try {
      const result = await Data.findOne({ status: true }).select(
        "hospitalID latitude longitude noOfBeds timestamp"
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
  router.post("/updateStatus", async (req, res) => {
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
  router.get("/getAllData", async (req, res) => {
    try {
        const allData = await Data.find();
        res.status(200).json(allData);
    } catch (error) {
        console.error("Error fetching data:", error);
        res.status(500).json({ error: "Failed to fetch data" });
    }
  });

module.exports = router;