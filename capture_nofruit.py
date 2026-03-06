import cv2
import os
import time

# Save path
SAVE_PATH = "dataset/Train/NoFruit"

# Folder create if not exists
os.makedirs(SAVE_PATH, exist_ok=True)

# Open webcam
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("Camera not opening ❌")
    exit()

count = 0
TOTAL_IMAGES = 200   # Kitni images leni hai
DELAY = 1            # 1 second gap

print("Starting capture... Look at different backgrounds.")
print("Press 'q' to stop early.")

while count < TOTAL_IMAGES:
    ret, frame = camera.read()
    if not ret:
        break

    # Show camera
    cv2.imshow("Capturing NoFruit Images", frame)

    # Save image
    filename = os.path.join(SAVE_PATH, f"nofruit_{count}.jpg")
    cv2.imwrite(filename, frame)

    count += 1
    print(f"Captured {count}/{TOTAL_IMAGES}")

    # Wait
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    time.sleep(DELAY)

camera.release()
cv2.destroyAllWindows()

print("✅ Capture Complete!")