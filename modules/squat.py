import mediapipe as mp
from utils import *
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class SquatEvaluator:
    def __init__(self):
        # current state: front
        self.front_counter = 0
        self.front_stage = "ongoing"
        self.min_ang_knee = 1000
        self.min_ang_hip = 10000

        # current state: side
        self.side_counter = 0 # due to missync issue
        self.side_stage = "ongoing" # due to missync issue
        self.side_min_ang_knee = 1000
        self.side_min_ang_hip = 10000

        # total criteria
        self.command = ""
        self.overall_criteria = {
            "criteria_1": False,
            "criteria_2": False,
            "criteria_3": False,
            "criteria_4": False,
            }

    def front_update(self, results):
        front_observation = self.get_front_obsevation(results)
        curr_knee_angle = front_observation["knee_angle"]
        curr_hip_angle = front_observation["hip_angle"]

        # ongoing: stack data
        if self.front_stage == 'ongoing': 
            self.angles_knee.append(curr_knee_angle)
            self.angles_hip.append(curr_hip_angle)
            
        # check_finish
        flag_finish = curr_knee_angle > min(self.angles_knee) and curr_knee_angle <= 90 
        if angle_knee <= 90 and self.front_stage =='ongoing':
            self.front_stage="finish"
            self.counter +=1
            # criteria 1: 
            min_angle_knee  = min(anngles_knee)
            if min_angle_knee > 0: 
                self.overall_criteria['criteria_1'] = True
            else:
                self.overall_criteria['criteria_1'] = False # reset / or keep? 
        
        if angle_knee > 169: # start next iteration
            self.front_stage = "ongoing"

   def get_front_observation(self, results):
        # Extract landmarks
        landmarks = results.pose_landmarks.landmark        
        # Get coordinates
        shoulder = [landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value].y]
        elbow = [landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].x,landmarks[mp_pose.PoseLandmark.LEFT_ELBOW.value].y]
        wrist = [landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].x,landmarks[mp_pose.PoseLandmark.LEFT_WRIST.value].y]
        
        # Get coordinates
        hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x,landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
    
        # Calculate angle
        angle = calculate_angle(shoulder, elbow, wrist)
        
        angle_knee = calculate_angle(hip, knee, ankle) #Knee joint angle
        angle_knee = round(angle_knee,2)
        
        angle_hip = calculate_angle(shoulder, hip, knee)
        angle_hip = round(angle_hip,2)
        
        hip_angle = 180-angle_hip
        knee_angle = 180-angle_knee

        observation_dict = {
                    "hip_angle": hip_angle,
                    "knee_angle": knee_angle
                    }
        return observation_dict

    def front_drawing(self, image, results): 
        cv2.putText(image, "Knee-joint angle : " + str(self.min_ang), 
                (30,100), # text position
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        cv2.putText(image, "Hip-joint angle : " + str(self.min_ang_hip), 
                (30,140), # text position
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2), 
                        mp_drawing.DrawingSpec(color=(203,17,17), thickness=2, circle_radius=2) 
                        )               
    
    def build_screen(self, screen, front_image, side_image):
        if self.front_stage = "up" and self.side_stage = "up": 
            direction_command = self.get_direction()
        return screen

    def get_direction(self):
        
        return command
        
