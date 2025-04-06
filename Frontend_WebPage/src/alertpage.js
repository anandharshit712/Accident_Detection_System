import React, { useEffect, useState } from 'react';
import axios from 'axios';

const hospitalID = localStorage.getItem('Hospital_ID'); // Replace with the desired hospital ID

function App() {
  const [alertData, setAlertData] = useState(null);
  const [logData, setLogData] = useState([]);

  // Polling every 5 seconds
  useEffect(() => {
    const interval = setInterval(() => {
      axios
        .get(`https://crash-api-six.vercel.app/api/hospstatus/${hospitalID}`)
        .then((res) => {
          if (res.data.status && (!alertData || res.data._id !== alertData._id)) {
              setAlertData(res.data);
              alert('🚨 Active status detected!');
          }
        })
        .catch(() => setAlertData(null));
    }, 1000);

    return () => clearInterval(interval);
  }, [alertData]);

  // Get logs
  useEffect(() => {
    axios
      .get(`https://crash-api-six.vercel.app/api/hospital-log/${hospitalID}`)
      .then((res) => setLogData(res.data))
      .catch((err) => console.error(err));
  }, [alertData]); // Refresh logs when alert data changes

  return (
    <div style={{ padding: 20 }}>
      <h2>Hospital Monitor for ID: {hospitalID}</h2>

      {alertData && (
        <div style={{ border: '1px solid red', padding: 10, marginBottom: 20 }}>
          <h4>🚨 Active Alert</h4>
          <pre>{JSON.stringify(alertData, null, 2)}</pre>
        </div>
      )}

      <h3>Log Data</h3>
      <table border="1" cellPadding="10">
        <thead>
          <tr>
            <th>Latitude</th>
            <th>Longitude</th>
            <th>Status</th>
            <th>Timestamp</th>
            <th>No. of Beds</th>
          </tr>
        </thead>
        <tbody>
          {logData.map((entry) => (
            <tr key={entry._id}>
              <td>{entry.lat}</td>
              <td>{entry.long}</td>
              <td>{entry.status ? 'True' : 'False'}</td>
              <td>{new Date(entry.timestamp).toLocaleString()}</td>
              <td>{entry.nofBeds}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export default App;
