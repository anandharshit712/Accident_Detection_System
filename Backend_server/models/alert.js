const mongoose = require('mongoose');

const alertSchema = new mongoose.Schema({
    hospitalID: { type: String, required: true },
    latitude: { type: Number, required: true },
    longitude: { type: Number, required: true },
    status: { type: Boolean, required: true },
    timestamp: { type: Date, default: Date.now },
    noOfBeds: { type: Number, required: true },
  });
  module.exports = mongoose.model("alert", alertSchema);

