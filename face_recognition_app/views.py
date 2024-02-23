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

        # Perform face detection or any other image processing tasks here

        # Compare image with user profiles
        identified_user = compare_with_user_profiles(image_rgb)

        if identified_user:
            return JsonResponse({'message': 'User found: {}'.format(identified_user.username)})  # Return the username of the identified user
        else:
            return JsonResponse({'message': 'User not found'})
    else:
        return JsonResponse({'error': 'Invalid request'})


def compare_with_user_profiles(image):
    # Get all user profiles
    user_profiles = UserProfile.objects.all()

    # Perform image comparison with user profiles
    for profile in user_profiles:
        # Implement image comparison logic (e.g., using OpenCV)
        pass

    # Placeholder return value
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