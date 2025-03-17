import mediapipe as mp
from utils import *
import cv2

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


class SquatEvaluator:
    def __init__(self):
        # current state: front
        self.front_count = 0
        self.front_state = "ongoing"
        self.angles_knee = []
        self.angles_hip = []
        
        # current state: side
        self.side_count = 0 # due to missync issue
        self.side_state = "ongoing" # due to missync issue
        # TODO

        # total criteria
        self.comment = "" # output command? # TODO
        self.overall_criteria = { # evaluation: pass or not
            "criteria_1": False,
            "criteria_2": False,
            "criteria_3": False,
            "criteria_4": False,
            }
        self.measure = {} # observation of deep position! 
        self.criteria_1_range = [40, 50]
        self.criteria_2_range = [40, 50]

    def front_update(self, results):
        curr_observation = self.get_front_observation(results)
        curr_knee_angle = curr_observation["knee_angle"]
        curr_hip_angle = curr_observation["hip_angle"]

        # ongoing: stack data
        if self.front_state == 'ongoing': 
            self.angles_knee.append(curr_knee_angle)
            self.angles_hip.append(curr_hip_angle)
            
        # finish & measuring with criteria!
        # finding deep pose!!
        flag_finish = curr_knee_angle > min(self.angles_knee) and curr_knee_angle <= 90 
        print('curr_knee', curr_knee_angle) # TODO: remoove this line
        if flag_finish and self.front_state =='ongoing':
            self.front_state="finish"
            self.front_count +=1

            # ex. criteria 1: 
            measurement_criteria_1 = min(self.angles_knee)
            self.measure['knee_angle'] = measurement_criteria_1
            if self.criteria_1_range[0] < measurement_criteria_1 and measurement_criteria_1 < self.criteria_1_range[1]:
                self.overall_criteria['criteria_1'] = True
            else:
                self.overall_criteria['criteria_1'] = False # reset / or keep? 

            # ex. crietria 2:
            self.measure['hip_angle'] = min(self.angles_hip)  # TODO: make your own criteria

            print(self.measure) # TODO: remove this line
        # add other criteria
        if curr_knee_angle > 169: # ready for next iteration
            self.front_state = "ongoing"
            self.angles_knee = [] 
            self.angles_hip = [] 
    
        return curr_observation

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
        
        #hip_angle = 180-angle_hip
        #knee_angle = 180-angle_knee
        observation_dict = {
                    "hip_angle": angle_hip,
                    "knee_angle": angle_knee,
                    "hip_coord": hip, 
                    "knee_coord": knee,
                    }
        return observation_dict

    def front_drawing(self, image, results, curr_observation): 

        angle_knee = curr_observation["knee_angle"]
        angle_hip = curr_observation["hip_angle"]
        coord_knee = curr_observation["knee_coord"] # 
        coord_hip = curr_observation["hip_coord"]

        cv2.putText(image, f"{angle_knee:.2f}",
                tuple(np.multiply(coord_knee, [1500, 800]).astype(int)), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2, cv2.LINE_AA)
            
        cv2.putText(image, f"{angle_hip:.2f}", 
                        tuple(np.multiply(coord_hip, [1500, 800]).astype(int)), 
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,0,0), 2, cv2.LINE_AA
                            )
        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS,
                        mp_drawing.DrawingSpec(color=(0,0,0), thickness=2, circle_radius=2), 
                        mp_drawing.DrawingSpec(color=(203,17,17), thickness=2, circle_radius=2) 
                        )               
    
    def build_screen(self, screen, front_image, side_image):
        ########################################################
        # step 1: get command
        ########################################################
        direction_comment = self.get_direction()

        ########################################################
        # step 2: image margin
        ########################################################
        margin = 20 # image borderline
        text_margin = 100 #위쪽 100px은 텍스트 공간
        screen_height, screen_width, _ = screen.shape
        # add margin & concat
        front_with_margin = cv2.copyMakeBorder(front_image, margin, margin, margin, margin, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        side_with_margin = cv2.copyMakeBorder(side_image, margin, margin, margin, margin, cv2.BORDER_CONSTANT, value=(0, 0, 0))
        combined_images = cv2.hconcat([front_with_margin, side_with_margin])
        # adjust image size
        if combined_images.shape[1] > screen_width or combined_images.shape[0] > screen_height:
            scale_x = screen_width / combined_images.shape[1]
            scale_y = (screen_height - text_margin) / combined_images.shape[0]  #
            scale = min(scale_x, scale_y)  # 비율 유지
            new_width = int(combined_images.shape[1] * scale)
            new_height = int(combined_images.shape[0] * scale)
            combined_images = cv2.resize(combined_images, (new_width, new_height), interpolation=cv2.INTER_AREA)

        ########################################################
        # step 3: build image
        ########################################################
        screen.fill(0)
        # stcik command
        cv2.putText(screen, direction_comment, (250, 50), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (255, 255, 255), 2)
        # stick images
        h, w, _ = combined_images.shape
        screen[-h:, (screen_width - w) // 2 : (screen_width + w) // 2] = combined_images
        return screen

    def get_direction(self):
        ##################################
        # just example 1 : TODO
        ##################################
        comment = f"count {max(self.front_count, self.side_count)}   "
        for k, v in self.measure.items():
            comment += f'{k}: {v:.2f}, '
        # example 2: pass or not
        #comment = f"count {max(self.front_count, self.side_count)}   "
        #for k, v in self.overall_criteria.items():
        #    comment += f'{k}: {v:}, '
        return comment
