import mediapipe as mp
from utils import *
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class SquatEvaluator:
    def __init__(self):
        self.count = 0
        # criteria
        self.min_ang = 1000
        self.min_ang_hip = 10000

        # Curl counter variables
        counter = 0 
        min_ang = 0
        max_ang = 0
        min_ang_hip = 0
        max_ang_hip = 0
        stage = None
        
    def get_observation(self, results):
        """
        input: results from mediapipe
        output: target_dict
        """
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

    def count(self, observation_dict):
       # Curl counter logic
        if angle_knee > 169:
            self.stage = "up"
        if angle_knee <= 90 and self.stage =='up':
            self.stage="down"
            counter +=1
            print(counter)
            min_ang  =min(self.angle_min)
            max_ang = max(self.angle_min)
            
            min_ang_hip  =min(self.angle_min_hip)
            max_ang_hip = max(self.angle_min_hip)
            
            print(min(angle_min), " _ ", max(angle_min))
            print(min(angle_min_hip), " _ ", max(angle_min_hip))
            angle_min = []
            angle_min_hip = [] 

    def render(self, image, results, observation_dict, save_video, save_path_per_img=None):
        cv2.rectangle(image, (20,20), (435,160), (0,0,0), -1)
        # Rep data
        cv2.putText(image, "Repetition : " + str(self.counter), 
                    (30,60), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        # Stage data
        cv2.putText(image, "Knee-joint angle : " + str(self.min_ang), 
                    (30,100), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        #Hip angle:
        cv2.putText(image, "Hip-joint angle : " + str(self.min_ang_hip), 
                    (30,140), 
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255,255,255), 2, cv2.LINE_AA)
        # Render detections
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                                mp_drawing.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2), 
                                mp_drawing.DrawingSpec(color=(203,17,17), thickness=2, circle_radius=2) 
                                 )               
        if save_path_per_img is not None: 
            breakpoint()
        else:
            cv2_vieo.write(image)
