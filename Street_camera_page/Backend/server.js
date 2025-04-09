const WebSocket = require("ws");

const wss = new WebSocket.Server({ port: 5000 });

wss.on("connection", (ws) => {
    console.log("New client connected");

    ws.on("message", (message) => {
        try {
            const parsedMessage = JSON.parse(message);

            // Broadcast to all connected clients
            wss.clients.forEach((client) => {
                if (client.readyState === WebSocket.OPEN) {
                    client.send(JSON.stringify(parsedMessage));
                }
            });

            //console.log("Received and Broadcast:", parsedMessage);
        } catch (err) {
            console.error("Error parsing message:", err);
        }
    });

    ws.on("close", () => console.log("Client disconnected"));
});

console.log("WebSocket server running on ws://localhost:5000");