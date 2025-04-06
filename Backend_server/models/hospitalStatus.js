const mongoose = require('mongoose');

const hospitalSchema = new mongoose.Schema({
    hID: { type: String, required: true },
    lat: { type: Number, required: true },
    long: { type: Number, required: true },
    status: { type: Boolean, required: true },
    timestamp: { type: Date, default: Date.now },
    nofBeds: { type: Number, required: true },
  });
  module.exports = mongoose.model('HospitalStatus', hospitalSchema);

