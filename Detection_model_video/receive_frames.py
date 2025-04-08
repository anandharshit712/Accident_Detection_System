import asyncio
import websockets
import json
import base64
import cv2
import numpy as np

async def get_frames():
    uri = "wss://camera-broadcast.onrender.com"
    async with websockets.connect(uri) as websocket:
        print("✅ Connected to WebSocket")

        while True:
            message = await websocket.recv()
            try:
                data = json.loads(message)
                if data["type"] == "image":
                    image_base64 = data["data"]
                    img_data = base64.b64decode(image_base64)
                    np_arr = np.frombuffer(img_data, dtype=np.uint8)
                    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
                    yield frame  # 👈 Yield the frame to be used elsewhere
                elif data["type"] == "info":
                    print("ℹ️ Stream Info:", data["data"])
            except Exception as e:
                print("❌ Error parsing message:", e)

async def run_inference_loop():
    async for frame in get_frames():
        # You now have `frame` as a decoded image
        # e.g., pass it to your CNN model
        print("🧠 Received frame shape:", frame.shape)

asyncio.run(run_inference_loop())

#
# import asyncio
# import websockets
# import json
# import base64
#
# async def receive_frames():
#     uri = "wss://camera-broadcast.onrender.com"
#     async with websockets.connect(uri) as websocket:
#         print("✅ Connected to WebSocket")
#
#         while True:
#             message = await websocket.recv()
#             try:
#                 data = json.loads(message)
#                 if data["type"] == "image":
#                     image_base64 = data["data"]
#                     print("📷 Received frame (Base64 length):", len(image_base64))
#                     # You can now decode and process this if needed
#                 elif data["type"] == "info":
#                     print("ℹ️ Stream Info:", data["data"])
#             except Exception as e:
#                 print("❌ Error parsing message:", e)
#
# asyncio.run(receive_frames())
