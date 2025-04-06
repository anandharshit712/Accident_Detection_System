const mongoose = require('mongoose');

const ambAlertSchema = new mongoose.Schema({
    ambulanceId: Number,
    status: Boolean,
    latitude: Number,
    longitude: Number,
  });
  module.exports = mongoose.model("ambAlert", ambAlertSchema);
