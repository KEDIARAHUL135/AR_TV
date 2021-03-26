#include "opencv2/opencv.hpp"
#include <opencv2/aruco.hpp>
#include <opencv2/core.hpp>
#include <opencv2/videoio.hpp>
#include <opencv2/highgui.hpp>
#include <opencv2/imgproc.hpp>
#include <opencv2/calib3d.hpp>
#include "opencv2/imgcodecs.hpp"
#include <iostream>
#include <stdio.h>
#include <vector>


bool FindBoxCoordinates(cv::Mat Frame, std::vector<cv::Point2f>& BoxCoordinates)
{
    // Detecting markers
    cv::Mat GrayFrame;
    cv::cvtColor(Frame, GrayFrame, cv::COLOR_BGR2GRAY);
    
    cv::Ptr<cv::aruco::Dictionary> ArucoDict = cv::aruco::getPredefinedDictionary(cv::aruco::DICT_6X6_50);

    std::vector<int> IDs;
    std::vector<std::vector<cv::Point2f>> Corners, RejectedCandidates;
    cv::Ptr<cv::aruco::DetectorParameters> Parameters = cv::aruco::DetectorParameters::create();
    cv::aruco::detectMarkers(Frame, ArucoDict, Corners, IDs, Parameters, RejectedCandidates);

    // If no aruco marker found or number of aruco merkers found is not 4, return None
    if (IDs.size() != 4)
        return false;


    // Storing Box coordinates
    for(int i = 0 ; i < 4 ; i++)
        BoxCoordinates.push_back(Corners[find(IDs.begin(), IDs.end(), i) - IDs.begin()][i]);

    return true;
}


void ProjectiveTransform(cv::Mat Frame, std::vector<cv::Point2f> Coordinates, cv::Mat& TransformedFrame)
{
    int Height = Frame.rows, Width = Frame.cols;

    cv::Point2f InitialPoints[4], FinalPoints[4];
    InitialPoints[0] = cv::Point2f(0, 0);
    InitialPoints[1] = cv::Point2f(Width - 1, 0);
    InitialPoints[2] = cv::Point2f(0, Height - 1);
    InitialPoints[3] = cv::Point2f(Width - 1, Height - 1);

    FinalPoints[0] = cv::Point2f(Coordinates[0].x, Coordinates[0].y);
    FinalPoints[1] = cv::Point2f(Coordinates[1].x, Coordinates[1].y);
    FinalPoints[2] = cv::Point2f(Coordinates[3].x, Coordinates[3].y);
    FinalPoints[3] = cv::Point2f(Coordinates[2].x, Coordinates[2].y);
    
    cv::Mat ProjectiveMatrix(2, 4, CV_32FC1);
    ProjectiveMatrix = cv::Mat::zeros(Height, Width, Frame.type());
    ProjectiveMatrix = cv::getPerspectiveTransform(InitialPoints, FinalPoints);

    cv::warpPerspective(Frame, TransformedFrame, ProjectiveMatrix, TransformedFrame.size());
}


void OverlapFrames(cv::Mat BaseFrame, cv::Mat SecFrame, std::vector<cv::Point2f> BoxCoordinates, cv::Mat& OverlapedFrame)
{
    // Finding transformed image
    cv::Mat TransformedFrame = BaseFrame.clone();
    ProjectiveTransform(SecFrame, BoxCoordinates, TransformedFrame);


    // Overlaping frames
    cv::Mat SecFrame_Mask = cv::Mat::zeros(cv::Size(BaseFrame.cols, BaseFrame.rows), BaseFrame.type());
    std::vector<cv::Point> BoxCoordinates_Converted;
    for (std::size_t i = 0; i < BoxCoordinates.size(); i++)
        BoxCoordinates_Converted.push_back(cv::Point(BoxCoordinates[i].x, BoxCoordinates[i].y));
    cv::fillConvexPoly(SecFrame_Mask, BoxCoordinates_Converted, cv::Scalar(255, 255, 255));

    cv::Mat SecFrame_Mask_not;
    cv::bitwise_not(SecFrame_Mask, SecFrame_Mask_not);
    cv::bitwise_and(BaseFrame, SecFrame_Mask_not, BaseFrame);
    OverlapedFrame = BaseFrame.clone();
    cv::bitwise_or(BaseFrame, TransformedFrame, OverlapedFrame);

}



int main()
{
    // Firstly, reading aruco video and the video for projection
    cv::VideoCapture ArucoVid_Cap, ProjVid_Cap;
    ArucoVid_Cap.open("Videos/ArucoVideo_OnWall.mp4");
    ProjVid_Cap.open("Videos/ProjVid.mpeg");

    // Creating video writer object
    cv::VideoWriter OutVid;
    OutVid.open("Videos/FinalVideo_cpp.mp4", static_cast<int>(ArucoVid_Cap.get(cv::CAP_PROP_FOURCC)), ArucoVid_Cap.get(cv::CAP_PROP_FPS), cv::Size(int(ArucoVid_Cap.get(3)), int(ArucoVid_Cap.get(4))));

    std::vector<int> SkippedFrames;         // record of skipped frames will be kept here

    while (true)
    {
        // Checking if all videos are opened.
        if (!ArucoVid_Cap.isOpened())
        {
            std::cout << "\nNot able to read aruco video.\n";
            exit(1);
        }
        if (!ProjVid_Cap.isOpened())
        {
            std::cout << "\nNot able to read projection video.\n";
            exit(2);
        }
                    
        // Reading frames
        cv::Mat ArucoVid_Frame, ProjVid_Frame;
        ArucoVid_Cap >> ArucoVid_Frame;
        ProjVid_Cap >> ProjVid_Frame;

        // End the output video if retArucoVid is false (video finished)
        if (ArucoVid_Frame.empty())
        {
            OutVid.release();
            std::cout << "\nStimulation Completed.\n";
            exit(3);
        }

        // Restart the projection video if finished
        if (ProjVid_Frame.empty())
        {
            ProjVid_Cap.set(cv::CAP_PROP_POS_FRAMES, 0);
            ProjVid_Cap >> ProjVid_Frame;
        }


        // Detecting Aruco markers in the frame
        std::vector<cv::Point2f> BoxCoordinates;
        bool ret = FindBoxCoordinates(ArucoVid_Frame, BoxCoordinates);

        // If aruco markers are not found, skip this frameand read next frame
        if (!ret)
        {
            // Storing the timestamp
            SkippedFrames.push_back(ArucoVid_Cap.get(cv::CAP_PROP_POS_MSEC));
            continue;
        }
            
        cv::Mat OverlapedFrame;
        OverlapFrames(ArucoVid_Frame, ProjVid_Frame, BoxCoordinates, OverlapedFrame);

        // Storing to output video
        OutVid.write(OverlapedFrame);

        // Displaying Output video
        cv::imshow("Output Video", OverlapedFrame);
        cv::waitKey(1);
    }

    // Releasing video objectsand destroying windows
    ArucoVid_Cap.release();
    ProjVid_Cap.release();
    OutVid.release();
    cv::destroyAllWindows();

    if (SkippedFrames.size() > 0)
    {
        std::cout << "\nFew frames were skipped because any or all aruco marker was not found.\n";
        for (int i = 0; i < SkippedFrames.size(); i++)
            std::cout << SkippedFrames[i] << std::endl;
    }

	return 0;
}