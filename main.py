import cv2
import numpy as np



def FindBoxCoordinates(Frame):
    # Detecting markers
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


def ProjectiveTransform(Frame, Coordinates, TransFrameShape):
    Height, Width = Frame.shape[:2]
    InitialPoints = np.float32([[0, 0], [Width-1, 0], [0, Height-1], [Width-1, Height-1]])
    FinalPoints = np.float32([Coordinates[0], Coordinates[1], Coordinates[3], Coordinates[2]])
    
    ProjectiveMatrix = cv2.getPerspectiveTransform(InitialPoints, FinalPoints)
    TransformedFrame = cv2.warpPerspective(Frame, ProjectiveMatrix, TransFrameShape[::-1])
    
    return TransformedFrame


def OverlapFrames(BaseFrame, SecFrame, BoxCoordinates):
    # Finding transformed image
    TransformedFrame = ProjectiveTransform(SecFrame, BoxCoordinates, BaseFrame.shape[:2])


    # Overlaping frames
    SecFrame_Mask = np.zeros(BaseFrame.shape, dtype=np.uint8)
    cv2.fillConvexPoly(SecFrame_Mask, np.asarray(BoxCoordinates, dtype=np.int32), (255, )*BaseFrame.shape[2])

    BaseFrame = cv2.bitwise_and(BaseFrame, cv2.bitwise_not(SecFrame_Mask))
    OverlapedFrame = cv2.bitwise_or(BaseFrame, TransformedFrame)
    
    return OverlapedFrame


if __name__ == "__main__":
    # Reading aruco video.
    ArucoVid_Cap = cv2.VideoCapture("Videos/ArucoVideo_OnWall.mp4")

    # Reading video for projection
    ProjVid_Cap = cv2.VideoCapture("Videos/ProjVid.mpeg")

    # Creating video writer object
    OutVid = cv2.VideoWriter('Videos/FinalVideo_py.avi', cv2.VideoWriter_fourcc(*'XVID'), ArucoVid_Cap.get(cv2.CAP_PROP_FPS), (int(ArucoVid_Cap.get(3)), int(ArucoVid_Cap.get(4)))) 

    SkippedFrames = []          # record of skipped frames will be kept here

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
        # (The output video will end when the input aruco video ends, not the projection video)
        if not retProjVid:
            ProjVid_Cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            retProjVid, ProjVid_Frame = ProjVid_Cap.read()

        
        # Detecting Aruco markers in the frame
        BoxCoordinates = FindBoxCoordinates(ArucoVid_Frame)

        # If aruco markers are not found, skip this frame and read next frame
        if BoxCoordinates is None:
            # Storing the timestamp
            SkippedFrames.append(ArucoVid_Cap.get(cv2.CAP_PROP_POS_MSEC))
            continue

        OverlapedFrame = OverlapFrames(ArucoVid_Frame, ProjVid_Frame, BoxCoordinates)

        # Storing to output video
        OutVid.write(OverlapedFrame)

        # Displaying Output video
        cv2.imshow("Output Video", OverlapedFrame)
        cv2.waitKey(1)

    # Releasing video objects and destroying windows
    ArucoVid_Cap.release()
    ProjVid_Cap.release()
    OutVid.release()
    cv2.destroyAllWindows()

    if len(SkippedFrames) > 0:
        print("Few frames were skipped because any or all aruco marker was not found.")
        print(SkippedFrames)

