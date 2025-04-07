const mongoose = require('mongoose');

const userSchema = new mongoose.Schema({
  h_ID: { type: Number, required: true},
  password: { type: String, required: true}
});

module.exports = mongoose.model('huserModel', userSchema);
