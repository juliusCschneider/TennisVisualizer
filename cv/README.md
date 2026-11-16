This repo is structured in two parts: The Computer Vision and Computer Graphics parts

The CV part consists of:
1. A yolo pose model to extract the joint positions
2. The server always served from a fixed position on the court (middle of the base line) so we do not need to estimate depth but know exactly where to place the generated character in openGL
3. Train a custom yolo network to find the tennis ball in the video and trace where it hits the field
Based on where it hits the field also visualise the ball in open GL.


TODO on CV part:
1. often the Bounce point is misidentified: def find_contact_and_bounce_frames(frames) needs to be adjusted since atm the point of contact to racket is identified as bounce.
2. 

