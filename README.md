# Sci-Fi Motion Detector

A Python-based real-time motion detector with a futuristic HUD aesthetic. This application uses computer vision to track hand movements and interact with a virtual "Energy Core".

## Features

-   **Real-time Hand Tracking**: Uses color segmentation to detect and track hand movements.
-   **Sci-Fi HUD**: Immersive full-screen interface with status indicators and dynamic overlays.
-   **Dynamic "Energy Core"**: A pulsating central object that reacts to proximity.
-   **Proximity Alert System**:
    -   **SAFE**: Green status, steady core pulse.
    -   **WARNING**: Yellow status, faster pulse, visual connection line.
    -   **DANGER**: Red status, critical alerts, rapid flashing.
-   **Full Screen Experience**: Automatically launches in full-screen mode for immersion.

## Prerequisites

-   Python 3.x
-   Webcam

## Installation

1.  Clone the repository or download the source code.
2.  Install the required dependencies:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

1.  Run the application:

    ```bash
    python main.py
    ```

2.  **Calibration**:
    -   A "Settings" window will appear (you may need to Alt-Tab to find it if it's behind the full screen).
    -   Adjust the HSV trackbars (`L - H`, `L - S`, `L - V`, etc.) to isolate your skin color. The default values are a starting point but lighting conditions vary.
    -   **Tip**: You want the "Mask" (if enabled in code) or the tracking to clearly show your hand as white and the background as black.

3.  **Interaction**:
    -   Move your hand towards the center of the screen.
    -   Watch the HUD state change from SAFE to WARNING to DANGER.

4.  **Controls**:
    -   Press `q` to quit the application.

## Troubleshooting

-   **Hand not detected?** Adjust the HSV trackbars in the Settings window. Lighting significantly affects color detection.
-   **Low FPS?** Ensure you are in a well-lit environment.

## Dependencies

-   `opencv-python`
-   `numpy`
