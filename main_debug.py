import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
import numpy as np
import argparse

from modules import *
from utils import *

mp_pose = mp.solutions.pose

def evaluate_pose(args):
    # Youtube video
    angle_min = []
    angle_min_hip = []
    cap = cv2.VideoCapture(args.video_path)

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    size = (640, 480) # TODO
    evaluator = get_pose_evaluator(args.workout)
    
    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap.isOpened():
            ret, frame = cap.read()
            if frame is not None:
                frame_ = rescale_frame(frame, percent=75)
            
            # Recolor image to RGB
            image = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
        
            # Make detection
            results = pose.process(image)
        
            # Recolor back to BGR
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

            observation = evaluator.get_observation(image, results)
            if args.debug: 
                break            
            break
            breakpoint()
    breakpoint()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_path", default='output.mp4')
    parser.add_argument("--video_path", default='youTube_video.mp4')
    parser.add_argument("--workout", default='squat')
    
    args = parser.parse_args()
    evaluate_pose(args)