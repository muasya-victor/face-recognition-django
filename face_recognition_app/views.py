from django.shortcuts import render
from django.http import JsonResponse
from .models import UserProfile
import base64
import numpy as np
import cv2
from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required

@login_required
def capture_image(request):
    return render(request, 'capture_image.html')


def compare_images(request):
    if request.method == 'POST' and 'image_data' in request.POST:
        # Get image data from POST request
        image_data = request.POST['image_data'].split(',')[1]

        # Convert base64 image data to numpy array
        image_bytes = base64.b64decode(image_data)
        image_np_array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

        # Convert BGR image to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Perform face recognition
        identified_user = compare_with_user_profiles(image_rgb)

        if identified_user:
            return JsonResponse({'message': 'User found: {}'.format(identified_user.username)})
        else:
            return JsonResponse({'message': 'User not found'})
    else:
        return JsonResponse({'error': 'Invalid request'})


def compare_with_user_profiles(image):
    # Get all user profiles
    user_profiles = UserProfile.objects.all()

    # Load the pre-trained face recognition model (e.g., LBPH)
    face_recognizer = cv2.face.LBPHFaceRecognizer_create()
    # Load the trained model weights
    face_recognizer.read("path/to/trained_model.xml")  # Update the path with your trained model

    # Convert the input image to grayscale (required for face recognition)
    gray_image = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Perform face recognition on the input image
    label, confidence = face_recognizer.predict(gray_image)

    # If confidence is below a certain threshold, consider it a match
    if confidence < 100:  # You may need to adjust this threshold based on your model's performance
        identified_user = UserProfile.objects.get(id=label)  # Assuming user ID corresponds to label
        return identified_user
    else:
        return None


def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('capture_image')  # Redirect to the desired page after login
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to the login page after logout