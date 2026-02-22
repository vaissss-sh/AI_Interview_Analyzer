import cv2
import mediapipe as mp
import numpy as np
import threading
import time

class VideoTracker(threading.Thread):
    def __init__(self, controller):
        super().__init__()
        self.controller = controller
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # EAR indices
        self.LEFT_EYE = [33, 160, 158, 133, 153, 144]
        self.RIGHT_EYE = [362, 385, 387, 263, 373, 380]
        
    def calculate_ear(self, landmarks, eye_indices):
        v1 = np.linalg.norm(np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y]) - 
                            np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y]))
        v2 = np.linalg.norm(np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y]) - 
                            np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y]))
        h = np.linalg.norm(np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y]) - 
                           np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y]))
        
        ear = (v1 + v2) / (2.0 * h)
        return ear

    def head_pose_estimation(self, landmarks, img_w, img_h):
        # 3D model points
        face_3d = []
        face_2d = []
        nose_idx = 1
        chin_idx = 152
        leye_idx = 33
        reye_idx = 263
        lmouth_idx = 61
        rmouth_idx = 291
        
        pose_indices = [nose_idx, chin_idx, leye_idx, reye_idx, lmouth_idx, rmouth_idx]
        
        for idx in pose_indices:
            lm = landmarks[idx]
            x, y = int(lm.x * img_w), int(lm.y * img_h)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])
            
        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)
        
        focal_length = 1 * img_w
        cam_matrix = np.array([ [focal_length, 0, img_h / 2],
                                [0, focal_length, img_w / 2],
                                [0, 0, 1]])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)
        
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        rmat, jac = cv2.Rodrigues(rot_vec)
        angles, mtxR, mtxQ, Qx, Qy, Qz = cv2.RQDecomp3x3(rmat)
        
        # x = pitch, y = yaw, z = roll
        pitch = angles[0] * 360
        yaw = angles[1] * 360
        roll = angles[2] * 360
        
        return pitch, yaw, roll

    def run(self):
        cap = cv2.VideoCapture(0)
        
        # Variables for tracking
        total_frames = 0
        eye_contact_frames = 0
        blink_count = 0
        ear_threshold = 0.22  # Below this is considered a blink
        is_blinking = False
        
        while self.controller.record_event.is_set():
            success, image = cap.read()
            if not success:
                print("Ignoring empty camera frame.")
                time.sleep(0.1)
                continue
                
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            image.flags.writeable = False
            results = self.face_mesh.process(image)
            image.flags.writeable = True
            image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
            
            img_h, img_w, img_c = image.shape
            
            if results.multi_face_landmarks:
                for face_landmarks in results.multi_face_landmarks:
                    # EAR & Blinks
                    left_ear = self.calculate_ear(face_landmarks.landmark, self.LEFT_EYE)
                    right_ear = self.calculate_ear(face_landmarks.landmark, self.RIGHT_EYE)
                    ear = (left_ear + right_ear) / 2.0
                    
                    if ear < ear_threshold:
                        if not is_blinking:
                            blink_count += 1
                            is_blinking = True
                    else:
                        is_blinking = False
                        
                    # Head Pose & Eye Contact
                    pitch, yaw, roll = self.head_pose_estimation(face_landmarks.landmark, img_w, img_h)
                    
                    total_frames += 1
                    # A rough threshold for eye contact: yaw and pitch within a certain degree range
                    if abs(yaw) < 15 and abs(pitch) < 15:
                        eye_contact_frames += 1
                        
            # Provide processed image back for UI
            # Compress image to reduce queue memory
            _, buffer = cv2.imencode('.jpg', image, [int(cv2.IMWRITE_JPEG_QUALITY), 50])
            frame_bytes = buffer.tobytes()
            
            # Put in queue (keep queue size 1 to prevent lag)
            if self.controller.vision_queue.full():
                try: 
                    self.controller.vision_queue.get_nowait()
                except: 
                    pass
            self.controller.vision_queue.put(frame_bytes)
            
        cap.release()
        
        # Process final vision metrics
        eye_contact_pct = (eye_contact_frames / total_frames) * 100 if total_frames > 0 else 0
        self.controller.update_state(
            blink_count=blink_count,
            eye_contact_percentage=eye_contact_pct
        )
