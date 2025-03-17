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
    
    size = (640, 1800) # TODO: change! 
    screen_height, screen_width = size[0], size[1]
    screen = np.zeros((screen_height, screen_width, 3), dtype=np.uint8) 

    # videos (outputs)
    if args.save_path: 
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
            curr_observation = evaluator.front_update(results)

            # drawing
            front_image.flags.writeable = True
            front_image = cv2.cvtColor(front_image, cv2.COLOR_RGB2BGR)
            evaluator.front_drawing(front_image, results, curr_observation)
            front_image.flags.writeable = False

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
            #curr_observation = evaluator.side_update(side_image, results)

            # drawing
            side_image.flags.writeable = True
            side_image = cv2.cvtColor(side_image, cv2.COLOR_RGB2BGR)
            evaluator.front_drawing(side_image, results, curr_observation)
            side_image.flags.writeable = False

            ########################################
            # step 3: aggregate
            ########################################
            full_image = evaluator.build_screen(screen, front_image, side_image)

            cv2.imshow('Evaluating your pose!', full_image)
            #cv2.imwrite('test.png', full_image)
            
            if args.save_path is not None:
                video_frames.write(full_image)

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

    parser.add_argument("--save_path", default=None, help="Path to save the output video")
    parser.add_argument("--front_video_path", default='youTube_video.mp4', help="Path to the front view video")
    parser.add_argument("--side_video_path", default='youTube_video.mp4', help="Path to the side view video")
    parser.add_argument("--workout", default='squat', help="Workout type")

    args = parser.parse_args()
    evaluate_pose(args)