import cv2
import numpy as np
import time
import math

def nothing(x):
    pass

class Visuals:
    def __init__(self):
        self.start_time = time.time()
        self.pulse_speed = 2.0
        
    def draw_hud(self, frame, state, fps):
        height, width = frame.shape[:2]
        color = (0, 255, 0)
        if state == "WARNING": color = (0, 255, 255)
        elif state == "DANGER": color = (0, 0, 255)
        
        # Border corners
        thickness = 4
        length = 40
        # Top Left
        cv2.line(frame, (10, 10), (10 + length, 10), color, thickness)
        cv2.line(frame, (10, 10), (10, 10 + length), color, thickness)
        # Top Right
        cv2.line(frame, (width - 10, 10), (width - 10 - length, 10), color, thickness)
        cv2.line(frame, (width - 10, 10), (width - 10, 10 + length), color, thickness)
        # Bottom Left
        cv2.line(frame, (10, height - 10), (10 + length, height - 10), color, thickness)
        cv2.line(frame, (10, height - 10), (10, height - 10 - length), color, thickness)
        # Bottom Right
        cv2.line(frame, (width - 10, height - 10), (width - 10 - length, height - 10), color, thickness)
        cv2.line(frame, (width - 10, height - 10), (width - 10, height - 10 - length), color, thickness)

        # Status Box
        cv2.rectangle(frame, (width//2 - 100, 20), (width//2 + 100, 70), (0, 0, 0), -1)
        cv2.rectangle(frame, (width//2 - 100, 20), (width//2 + 100, 70), color, 2)
        
        font = cv2.FONT_HERSHEY_SIMPLEX
        text_size = cv2.getTextSize(state, font, 1, 2)[0]
        text_x = (width - text_size[0]) // 2
        cv2.putText(frame, state, (text_x, 55), font, 1, color, 2)

        
        cv2.putText(frame, f"FPS: {int(fps)}", (20, 40), font, 0.7, (0, 255, 0), 1)
        
        # Danger
        if state == "DANGER":
            # Flashing border effect
            if int(time.time() * 10) % 2 == 0:
                cv2.rectangle(frame, (0, 0), (width, height), (0, 0, 255), 10)
                cv2.putText(frame, "CRITICAL PROXIMITY", (width//2 - 200, height - 100), font, 1.5, (0, 0, 255), 3)

    def draw_energy_core(self, frame, center, base_radius, state):
        elapsed = time.time() - self.start_time
        
        color = (255, 0, 0) 
        pulse_mag = 5
        
        if state == "WARNING":
            color = (0, 255, 255)
            self.pulse_speed = 5.0
            pulse_mag = 10
        elif state == "DANGER":
            color = (0, 0, 255)
            self.pulse_speed = 10.0
            pulse_mag = 15
        else:
            self.pulse_speed = 2.0
            
        # Pulsating 
        pulse = math.sin(elapsed * self.pulse_speed) * pulse_mag
        radius = int(base_radius + pulse)
        
        # Outer core
        cv2.circle(frame, center, radius, color, 2)
        cv2.circle(frame, center, radius + 10, color, 1)
        
        # Inner Core
        cv2.circle(frame, center, int(base_radius * 0.5), color, -1)
        cv2.putText(frame, "CORE", (center[0] - 25, center[1] + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

def main():
    cap = cv2.VideoCapture(0)

    window_name = 'Motion Detector'
    cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
    cv2.setWindowProperty(window_name, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
    
    cv2.namedWindow('Settings')
    cv2.resizeWindow('Settings', 300, 300)
    
    # Trackbars
    cv2.createTrackbar('L - H', 'Settings', 0, 179, nothing)
    cv2.createTrackbar('L - S', 'Settings', 48, 255, nothing)
    cv2.createTrackbar('L - V', 'Settings', 80, 255, nothing)
    cv2.createTrackbar('U - H', 'Settings', 20, 179, nothing)
    cv2.createTrackbar('U - S', 'Settings', 255, 255, nothing)
    cv2.createTrackbar('U - V', 'Settings', 255, 255, nothing)

    visuals = Visuals()
    
    prev_frame_time = 0
    
    hand_pos_history = []
    MAX_HISTORY = 5

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        
        # FPS
        new_frame_time = time.time()
        fps = 1/(new_frame_time-prev_frame_time) if prev_frame_time > 0 else 0
        prev_frame_time = new_frame_time

        # HSV 
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        l_h = cv2.getTrackbarPos('L - H', 'Settings')
        l_s = cv2.getTrackbarPos('L - S', 'Settings')
        l_v = cv2.getTrackbarPos('L - V', 'Settings')
        u_h = cv2.getTrackbarPos('U - H', 'Settings')
        u_s = cv2.getTrackbarPos('U - S', 'Settings')
        u_v = cv2.getTrackbarPos('U - V', 'Settings')

        lower_range = np.array([l_h, l_s, l_v])
        upper_range = np.array([u_h, u_s, u_v])
        
        mask = cv2.inRange(hsv, lower_range, upper_range)
        kernel = np.ones((5, 5), np.uint8)
        mask = cv2.erode(mask, kernel, iterations=1)
        mask = cv2.dilate(mask, kernel, iterations=2)

        # Object 
        obj_center = (width // 2, height // 2)
        obj_radius = 60
        
        # Hand 
        contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        
        state = "SAFE"
        hand_center = None

        if contours:
            max_contour = max(contours, key=cv2.contourArea)
            if cv2.contourArea(max_contour) > 1000:
                M = cv2.moments(max_contour)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    
                    hand_pos_history.append((cx, cy))
                    if len(hand_pos_history) > MAX_HISTORY:
                        hand_pos_history.pop(0)
                    
                    avg_cx = int(sum(p[0] for p in hand_pos_history) / len(hand_pos_history))
                    avg_cy = int(sum(p[1] for p in hand_pos_history) / len(hand_pos_history))
                    hand_center = (avg_cx, avg_cy)

                    # Draw Hand
                    cv2.drawContours(frame, [max_contour], -1, (0, 255, 0), 2)
                    cv2.line(frame, hand_center, (hand_center[0]+20, hand_center[1]-20), (0, 255, 0), 2)
                    cv2.putText(frame, "TARGET", (hand_center[0]+25, hand_center[1]-25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
                    
                    # Distance 
                    distance = np.sqrt((avg_cx - obj_center[0])**2 + (avg_cy - obj_center[1])**2)
                    
                    if distance < obj_radius + 60:
                        state = "DANGER"
                    elif distance < obj_radius + 200:
                        state = "WARNING"
                        # Draw line 
                        cv2.line(frame, hand_center, obj_center, (0, 255, 255), 1)

        
        visuals.draw_energy_core(frame, obj_center, obj_radius, state)
        visuals.draw_hud(frame, state, fps)

        cv2.imshow(window_name, frame)
        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
