import React, { useState, useEffect } from "react";
import axios from "axios";
const au =require("./sound/lol.mp3")


function AlertPage() {
    const [formData, setFormData] = useState({
        mobileNumber: "",
        latitude: "",
        longitude: "",
        status: false,
        noOfBeds: 0,
    });

    const [data, setData] = useState([]);
    const [alertData, setAlertData] = useState(null);

    const handleChange = (e) => {
        const { name, value } = e.target;
        setFormData((prevData) => ({
            ...prevData,
            [name]: name === "status" ? e.target.checked : value,
        }));
    };

   

    const fetchData = async () => {
        try {
            const response = await axios.get("https://accident-cisl.onrender.com/getAllData");
            setData(response.data);
        } catch (error) {
            console.error("Error fetching data:", error);
        }
    };

    const checkStatus = async () => {
        try {
            const response = await axios.get("https://accident-cisl.onrender.com/checkStatus");
            if (response.data && response.data.mobileNumber) {
                setAlertData(response.data);
                playAlertSound();
                
                alert(`Alert!
                    Mobile Number: ${response.data.mobileNumber}
                    Latitude: ${response.data.latitude}
                    Longitude: ${response.data.longitude}
                    Beds: ${response.data.noOfBeds}`);
                    console.log(alertData._id);
                } else {
                    setAlertData(null);
                }
                fetchData();
            } catch (error) {
                console.error("Error checking status:", error);
            }
        };
        
        
        
        const playAlertSound = () => {
        
        // const audio = new Audio("./sound/lol.mp3");
        // audio.play();
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(checkStatus, 5000);
        return () => clearInterval(interval);
    }, []);

    return (<>

<div class="container2">
        <div className="AlertPage">
            <h2>All Data</h2>
            <table border="1">
                <thead>
                    <tr>
                        <th>Mobile Number</th>
                        <th>Latitude</th>
                        <th>Longitude</th>
                        <th>Status</th>
                        <th>Timestamp</th>
                        <th>No. of Beds Required</th>
                    </tr>
                </thead>
                <tbody>
                    {data.map((item) => (
                        <tr key={item._id}>
                            <td>{item.mobileNumber}</td>
                            <td>{item.latitude}</td>
                            <td>{item.longitude}</td>
                            <td>{item.status ? "True" : "False"}</td>
                            <td>{new Date(item.timestamp).toLocaleString()}</td>
                            <td>{item.noOfBeds}</td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
        </div>
                    </>
    );
}

export default AlertPage;