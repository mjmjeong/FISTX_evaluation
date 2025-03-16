import cv2
from cv2 import destroyAllWindows
import mediapipe as mp
import numpy as np
import argparse

from modules import *
from utils import *

mp_pose = mp.solutions.pose

def evaluate_pose(args):
    # init evaluator
    evaluator = get_pose_evaluator(args.workout)

    # read front video
    cap_front = cv2.VideoCapture(args.front_video_path)
    width_front = int(cap_front.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height_front = int(cap_front.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)

    # read side video
    cap_side = cv2.VideoCapture(args.side_video_path)
    width_side = int(cap_side.get(cv2.CAP_PROP_FRAME_WIDTH) + 0.5)
    height_side = int(cap_side.get(cv2.CAP_PROP_FRAME_HEIGHT) + 0.5)
    
    # videos (outputs)
    if args.save_path: 
        size = (640, 480) # TODO: change! 
        fourcc = cv2.VideoWriter_fourcc('m', 'p', '4', 'v')
        video_frames = cv2.VideoWriter(args.save_path, fourcc, 24, size)

    with mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5) as pose:
        while cap_front.isOpened():
            #################################
            # step 1: front
            #################################
            ret, frame = cap_front.read()
            if not ret:
                break
            if frame is not None:
                frame_ = rescale_frame(frame, percent=75)
            
            # measure
            front_image = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            front_image.flags.writeable = False
            results = pose.process(front_image)
            evaluator.front_update(front_image, results)

            # drawing
            front_image.flags.writeable = True
            front_image = cv2.cvtColor(front_image, cv2.COLOR_RGB2BGR)
            evaluator.front_drawing(front_image, results)
            front _image.flags.writeable = False

            #################################
            # step 2: side
            #################################
            ret, frame = cap_side.read()
            if not ret:
                break
            if frame is not None:
                frame_ = rescale_frame(frame, percent=75)
            
            # measure
            side_image = cv2.cvtColor(frame_, cv2.COLOR_BGR2RGB)
            side_image.flags.writeable = False
            results = pose.process(side_image)
            evaluator.side_update(side_image, results)

            # drawing
            side_image.flags.writeable = True
            side_image = cv2.cvtColor(side_image, cv2.COLOR_RGB2BGR)
            evaluator.front_drawing(side_image, results)
            side_image.flags.writeable = False

            ########################################
            # step 3: aggregate
            ########################################
            full_image = evaluator.build_screen(front_image, side_image)
            cv2.imshow('Evaluating your pose!', full_image)
            video_frames.write(image)
    
            if cv2.waitKey(10) & 0xFF == ord('q'):
                cap_front.release()
                cap_side.release()
                video_frames.release()
                cv2.destroyAllWindows()

    cap_front.release() # detach allocate 
    cap_side.release() # detach allocate 
    cv2.destroyAllWindows()
    # saving local video
   
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--save_path", default='output.mp4')
    parser.add_argument("--front_video_path", default='youTube_video.mp4')
    parser.add_argument("--side_video_path", default='youTube_video.mp4')
    parser.add_argument("--workout", default='squat')
    
    args = parser.parse_args()
    evaluate_pose(args)