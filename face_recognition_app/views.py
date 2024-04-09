from django.shortcuts import render
from django.http import JsonResponse
from .models import UserProfile , CustomUser
import numpy as np
import matplotlib.pyplot as plt
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
import cv2 
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404
from django.template.loader import get_template
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import RecognitionHistory
import base64


def get_custom_user_by_username(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

@login_required
def compare_image(request):
    if request.method == 'POST':
        # Get the captured image from the request
        captured_image = request.FILES['captured_image']


        RecognitionHistory.objects.create(recognition_image=captured_image)
        last_uploaded_image = RecognitionHistory.objects.last()

        # Convert the captured image to a numpy array
        captured_image_array = np.array(cv2.imread(str(last_uploaded_image.recognition_image)))

        # Get all the images from the database
        db_images = UserProfile.objects.all()
        print(db_images)

        # Initialize a list to store the similarity scores
        similarity_scores = []

        # Loop through all the images in the database
        for db_image in db_images:
            # Convert the database image to a numpy array
            db_image_array = np.array(cv2.imread(db_image.profile_picture.path))

            # Calculate the similarity score between the captured image and the database image
            similarity_score = cv2.compareHist(cv2.calcHist([captured_image_array], [0], None, [64], [0, 256]),
                                              cv2.calcHist([db_image_array], [0], None, [64], [0, 256]),
                                              cv2.HISTCMP_CORREL) * 100

            # Append the similarity score to the list
            similarity_scores.append(similarity_score)

        # Get the index of the most similar image in the database
        most_similar_index = np.argmax(similarity_scores)

        # Get the most similar image from the database
        most_similar_image = db_images[int(most_similar_index)]
        print(most_similar_image.user)
        print(
            get_custom_user_by_username(most_similar_image.user.username),
            similarity_scores[most_similar_index],
            "userrrrr"
        )
        print(f"Most similar image: {most_similar_image.user.username}, match percentage: {similarity_scores[most_similar_index]:.2f}%")

      
        if similarity_scores[most_similar_index] > 96 :
            # Return the most similar image to the user
            return render(request, 'compare_result.html', {'user': most_similar_image})
        else:
            return render(request, 'does_not_exist.html')


    return render(request, 'compare_image.html')



# def compare_images(request):
#     if request.method == 'POST' and 'user_id' in request.POST:
#         user_id = request.POST['user_id']
        
#         # Get UserProfile object based on user_id
#         user_profile = UserProfile.objects.filter(user_id=user_id).first()

#         if user_profile and user_profile.profile_picture:
#             # Read the image data from the profile_picture field
#             image_data = user_profile.profile_picture.read()

#             # Convert base64 image data to NumPy array
#             try:
#                 image_np_array = np.frombuffer(image_data, dtype=np.uint8)

#                 # Decode the image array to OpenCV format
#                 image = cv2.imdecode(image_np_array, cv2.IMREAD_COLOR)

#                 # Convert the input image to RGB (assuming it's in BGR format)
#                 image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

#                 # Perform face recognition or other processing
#                 identified_user = compare_with_user_profiles(image_rgb)

#                 if identified_user:
#                     user_details = {
#                         'username': identified_user.username,
#                         'email': identified_user.email,
#                         'first_name': identified_user.first_name,
#                         'last_name': identified_user.last_name,
#                         # Add more user details as needed
#                     }
#                     print(user_details)
#                     return JsonResponse({'message': 'User found', 'user_details': user_details})
#                 else:
#                     return JsonResponse({'message': 'User not found'})

#             except Exception as e:
#                 return JsonResponse({'error': f'Error processing image: {e}'}, status=400)

#         else:
#             return JsonResponse({'message': 'User profile not found or profile picture is empty'}, status=400)

#     else:
#         return JsonResponse({'error': 'Invalid request'}, status=400)



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


@login_required

def report(request):
    user = request.user
    users = CustomUser.objects.all()
    context  = {"users": users}
    if user is not None:
        if user.is_superuser:
            return render(request, 'admin.html', context)
        else:
            return redirect('compare-images/')
        
    else:
        return redirect('login/')


def generate_pdf(request):
    # Retrieve data for the PDF from the database or any other source
    users = CustomUser.objects.all()
    context = {"users": users}

    # Render template
    template = get_template('admin.html')
    html = template.render(context)

    # Create PDF file
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="admin_report.pdf"'

    # Generate PDF from HTML content
    pisa_status = pisa.CreatePDF(html, dest=response)

    # If PDF generation failed, return an error message
    if pisa_status.err:
        return HttpResponse('PDF generation error!')

    return response