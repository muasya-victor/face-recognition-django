import json

from deepface import DeepFace

result = DeepFace.verify(img1_path = "gili.jpg", img2_path = "profile_pictures/test.jpg")

print(json.dumps(result, indent=2))