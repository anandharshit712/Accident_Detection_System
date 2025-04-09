import React, { useRef, useState, useEffect } from "react";
import Webcam from "react-webcam";
import './styles.css';  // Import the CSS file

const Sender = () => {
    const webcamRef = useRef(null);
    const ws = useRef(null);
    const [streaming, setStreaming] = useState(false);

    useEffect(() => {
        ws.current = new WebSocket("wss://websocket-server-j3jb.onrender.com");

        ws.current.onopen = () => console.log("Connected to WebSocket");
        ws.current.onclose = () => console.log("Disconnected from WebSocket");

        return () => ws.current.close();
    }, []);

    const startStreaming = () => {
        if (ws.current.readyState === WebSocket.OPEN) {
            // Get device location
            navigator.geolocation.getCurrentPosition((position) => {
                const data = {
                    id: 8046, // Random ID
                    latitude: position.coords.latitude,
                    longitude: position.coords.longitude
                };
                ws.current.send(JSON.stringify({ type: "info", data }));
                console.log("Sent Initial Data:", data);
            });
        }

        //camera stream
        if (webcamRef.current) {
            navigator.mediaDevices.getUserMedia({ video: true })
                .then((stream) => {
                    webcamRef.current.video.srcObject = stream; // Reattach the video stream
                })
                .catch((error) => console.error("Error accessing webcam:", error));
        }

        setStreaming(true);
    };

    const stopStreaming = () => {
        setStreaming(false);

        // Stop the webcam stream
        if (webcamRef.current && webcamRef.current.video) {
            const stream = webcamRef.current.video.srcObject;
            if (stream) {
                stream.getTracks().forEach(track => track.stop()); // Stop all tracks, camera off hai
                webcamRef.current.video.srcObject = null; // Clear webcam, screen se htane ke liye
            }
        }
    };

    useEffect(() => {
        let interval;
        if (streaming) {
            interval = setInterval(() => {
                if (webcamRef.current) {
                    const imageSrc = webcamRef.current.getScreenshot();
                    if (imageSrc && ws.current.readyState === WebSocket.OPEN) {
                        ws.current.send(JSON.stringify({ type: "image", data: imageSrc }));
                        console.log("Sent Image:", imageSrc.slice(0, 30) + "...");
                    }
                }
            }, 200);
        }
        return () => clearInterval(interval);
    }, [streaming]);

    return (
        <div className="container"> {/* Apply the container class */}
            <div>
                <h2>Live Camera Feed - Sender</h2>
                <Webcam
                    className="webcam-container"
                    ref={webcamRef}
                    screenshotFormat="image/jpeg"
                    width={400}
                    height={300}
                    videoConstraints={{ facingMode: "user" }}
                />
                <br />
                <button onClick={streaming ? stopStreaming : startStreaming}>
                    {streaming ? "Stop Streaming" : "Start Streaming"}
                </button>
            </div>
        </div>
    );
};

export default Sender;
