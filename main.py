import os
import cv2
import numpy as np



def FindBoxCoordinates(Frame):
    # Detecting markerrs
    GrayFrame = cv2.cvtColor(Frame,cv2.COLOR_BGR2GRAY)
    ArucoDict = cv2.aruco.Dictionary_get(cv2.aruco.DICT_6X6_50)
    Parameters = cv2.aruco.DetectorParameters_create()
    Corners, IDs, RejectedImgPoints = cv2.aruco.detectMarkers(GrayFrame, ArucoDict, parameters=Parameters)

    # If no aruco marker found or number of aruco merkers found is not 4, return None
    if IDs is None:
        return None
    if len(IDs) != 4:
        return None

    # Storing Box coordinates
    BoxCoordinates = []
    for i in range(4):
        BoxCoordinates.append(Corners[int(np.where(IDs == i)[0])][0][i])

    return BoxCoordinates    


if __name__ == "__main__":
    # Firstly, reading aruco video.
    ArucoVid_Cap = cv2.VideoCapture("Videos/ArucoVideo_OnWall.mp4")

    # Reading video for projection
    ProjVid_Cap = cv2.VideoCapture("Videos/ProjVid.mpeg")

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
        
        # Reading frames
        retArucoVid, ArucoVid_Frame = ArucoVid_Cap.read()
        retProjVid, ProjVid_Frame = ProjVid_Cap.read()

        # End the output video if retArucoVid is false (video finished)
        if not retArucoVid:
            OutVid.release()
            print("Stimulation Completed.")
            exit()

        # Restart the projection video if finished
        if not retProjVid:
            ProjVid_Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            retProjVid, ProjVid_Frame = ProjVid_Cap.read()

        
        # Detecting Aruco markers in the frame
        BoxCoordinates = FindBoxCoordinates(ArucoVid_Frame)