import os
import cv2
import numpy as np



if __name__ == "__main__":
    # Firstly, reading aruco video.
    ArucoVid_Cap = cv2.VideoCapture("Videos/ArucoVideo.avi")

    # Reading video for projection
    ProjVid_Cap = cv2.VideoCapture("Videos/ProjVid1.mpeg")

    # Creating video writer object
    OutVid = cv2.VideoWriter('Videos/FinalVideo.avi', cv2.VideoWriter_fourcc(*'XVID'), ArucoVid_Cap.get(cv2.CAP_PROP_FPS), (int(ArucoVid_Cap.get(3)), int(ArucoVid_Cap.get(4)))) 


    while True:
        # Checking if all videos are opened.
        if not ArucoVid_Cap.isOpened():
            print("Not able to read aruco video.")
            exit()
        if not ProjVid_Cap.isOpened():
            print("Not able to read projection video.")
            exit()
        
        exit()