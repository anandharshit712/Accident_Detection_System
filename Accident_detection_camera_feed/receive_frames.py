# import asyncio
# import websockets
# import json
# import base64
# import cv2
# import numpy as np
#
# # async def get_frames():
# #     uri = "wss://camera-broadcast.onrender.com"
# #     async with websockets.connect(uri) as websocket:
# #         print("✅ Connected to WebSocket")
# #
# #         while True:
# #             message = await websocket.recv()
# #             try:
# #                 data = json.loads(message)
# #                 if data["type"] == "image":
# #                     image_base64 = data["data"]
# #                     img_data = base64.b64decode(image_base64)
# #                     np_arr = np.frombuffer(img_data, dtype=np.uint8)
# #                     frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
# #                     yield frame  # 👈 Yield the frame to be used elsewhere
# #                 elif data["type"] == "info":
# #                     print("ℹ️ Stream Info:", data["data"])
# #             except Exception as e:
# #                 print("❌ Error parsing message:", e)
#
# async def get_frames():
#     uri = "wss://camera-broadcast.onrender.com"
#     async with websockets.connect(uri) as websocket:
#         print("✅ Connected to WebSocket")
#
#         while True:
#             message = await websocket.recv()
#             try:
#                 data = json.loads(message)
#                 if data["type"] == "image":
#                     print("📷 Frame received.")
#                     image_base64 = data["data"]
#                     img_data = base64.b64decode(image_base64)
#                     np_arr = np.frombuffer(img_data, dtype=np.uint8)
#                     frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
#                     if frame is None:
#                         print("❌ Failed to decode frame.")
#                     yield frame
#                 elif data["type"] == "info":
#                     print("ℹ️ Stream Info:", data["data"])
#             except Exception as e:
#                 print("❌ Error parsing message:", e)


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
            try:
                message = await websocket.recv()
                data = json.loads(message)

                if data["type"] == "image":
                    image_base64 = data["data"]

                    # Sanitize and decode
                    try:
                        image_base64 = image_base64.split(",")[-1]  # Remove prefix if exists (like data:image/jpeg;base64,...)
                        img_data = base64.b64decode(image_base64)

                        # Convert to np array and decode
                        np_arr = np.frombuffer(img_data, dtype=np.uint8)
                        frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

                        if frame is not None:
                            yield frame
                        else:
                            print("❌ Failed to decode image: cv2.imdecode returned None")

                    except Exception as e:
                        print(f"❌ Decoding error: {e}")

                elif data["type"] == "info":
                    print("ℹ️ Stream Info:", data["data"])

            except Exception as e:
                print(f"❌ General WebSocket error: {e}")
                await asyncio.sleep(1)
