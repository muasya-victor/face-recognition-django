from django.shortcuts import render
from django.http import JsonResponse
from .models import UserProfile , CustomUser
import base64
import numpy as np
import cv2
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model

@login_required
def capture_image(request):
    # Get the last entry in the CustomUser model
    last_user = "no user found"
    last_user = CustomUser.objects.last()

    # Check if last_user exists and extract first_name and last_name
    if last_user:
        first_name = last_user.first_name
        last_name = last_user.last_name
    else:
        first_name = "no "
        last_name = " user found"

    context = {
        'first_name': first_name,
        'last_name': last_name,
    }

    return render(request, 'capture_image.html', context)
def compare_images(request):
    if request.method == 'POST' and 'user_id' in request.POST:
        user_id = request.POST['user_id']
        
        # Get UserProfile object based on user_id
        user_profile = UserProfile.objects.filter(user_id=user_id).first()

        if user_profile and user_profile.profile_picture:
            # Read the image data from the profile_picture field
            image_data = user_profile.profile_picture.read()

            # Convert base64 image data to NumPy array
            try:
                image_np_array = np.frombuffer(image_data, dtype=np.uint8)

                # Decode the image array to OpenCV format
                image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

                # Convert the input image to RGB (assuming it's in BGR format)
                image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

                # Perform face recognition or other processing
                identified_user = compare_with_user_profiles(image_rgb)

                if identified_user:
                    user_details = {
                        'username': identified_user.username,
                        'email': identified_user.email,
                        'first_name': identified_user.first_name,
                        'last_name': identified_user.last_name,
                        # Add more user details as needed
                    }
                    print(user_details)
                    return JsonResponse({'message': 'User found', 'user_details': user_details})
                else:
                    return JsonResponse({'message': 'User not found'})

            except Exception as e:
                return JsonResponse({'error': f'Error processing image: {e}'}, status=400)

        else:
            return JsonResponse({'message': 'User profile not found or profile picture is empty'}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request'}, status=400)

def compare_with_user_profiles(request):
    # env = Env()
    # env.read_env()  # Load environment variables from .env file

    CustomUser = get_user_model()

    if request.method == 'POST' and 'user_id' in request.POST:
        user_id = request.POST['user_id']
        
        # Get UserProfile object based on user_id
        user_profile = get_object_or_404(UserProfile, user_id=1)

        # Check if the profile_picture field is not empty
        if user_profile.profile_picture:
            # Read the image data from the profile_picture field
            image_data = user_profile.profile_picture.read()

            # Convert base64 image data to NumPy array
            try:
                image_np_array = np.frombuffer(image_data, dtype=np.uint8)

                # Decode the image array to OpenCV format
                image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

                # Convert the input image to grayscale
                gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

                # Process the image (e.g., face detection and recognition)
                # ...
                
                # Example response for demonstration
                response_data = {'message': 'Image processed successfully'}
                return JsonResponse(response_data)

            except Exception as e:
                error_message = f"Error processing image: {e}"
                return JsonResponse({'error': error_message}, status=400)
        
        else:
            return JsonResponse({'error': 'Profile picture not found or empty'}, status=400)

    else:
        return JsonResponse({'error': 'Invalid request method or missing user_id'}, status=400)
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