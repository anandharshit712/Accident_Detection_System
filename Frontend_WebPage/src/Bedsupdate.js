import React, { useState, useEffect } from 'react';
import {Link, useNavigate } from "react-router-dom";
import axios from 'axios';
import "./dbs.css"

const Bedsupdate = () => {
  const navigate = useNavigate();
  //const [hospitalID, setHospitalID] = useState('');
  const [hospitalData, setHospitalData] = useState(null);
  const [beds, setBeds] = useState('');
  const hospitalID= localStorage.getItem('Hospital_ID');

  // Fetch Hospital by ID
  const fetchHospital = async () => {
    try {
      const response = await axios.get(`https://crash-api-six.vercel.app/hospital/${hospitalID}`);
      setHospitalData(response.data);
      setBeds(response.data.no_of_available_beds);
    } catch (error) {
      console.error(error);
      setHospitalData(null);
    }
  };
   
  useEffect(() => {
    fetchHospital();
      }, []);

  // Update Beds
  const updateBeds = async () => {
    try {
      const response = await axios.patch(`https://crash-api-six.vercel.app/hospital/${hospitalID}`, {
        no_of_available_beds: beds
      });
      setHospitalData(response.data);
      alert('Beds updated successfully');
    } catch (error) {
      console.error(error);
      alert('Error updating beds');
    }
  };

  const logout=()=>{
    setTimeout(()=>{navigate("/")},500);
    localStorage.removeItem('Hospital_ID');
  }

  return (
    <>
      <h1>Hospital Bed Management</h1>
      
      <div class="container">
      <div>
        {/* <input
          type="number"
          placeholder="Enter Hospital ID"
          value={hospitalID}
          onChange={(e) => setHospitalID(e.target.value)}
        /> */}
        <button onClick={logout}>Log Out</button>
      </div>
        <div>

          <p class="result" id="updateResult">{/* Display Hospital Details */}
            {hospitalData && (
              <div style={{ marginTop: '20px' }}>
                <h3>Hospital Details</h3>
                <p>Hospital ID: {hospitalData.hospitalID}</p>
                <p>Latitude: {hospitalData.latitude}</p>
                <p>Longitude: {hospitalData.longitude}</p>
        <div>

          <h3>Update Beds</h3>
          <p class="result" id="bedStatus"><p>Total Beds: {hospitalData.total_of_available_beds}</p>
            <p>Available Beds: {hospitalData.no_of_available_beds}</p></p>
        </div>


                {/* Update Beds */}
                <div>
                  <input
                    type="number"
                    placeholder="Update Available Beds"
                    value={beds}
                    onChange={(e) => setBeds(e.target.value)}
                  />
                  <button onClick={updateBeds}>Update Beds</button>
                </div>
              </div>
            )}</p>
        </div>
      </div>
      
    </>
  );
};

export default Bedsupdate;
