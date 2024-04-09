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

        # Perform face detection on the captured image
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces_captured = face_cascade.detectMultiScale(captured_image_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

        if len(faces_captured) == 0:
            return render(request, 'does_not_exist.html')

        # Resize and crop the detected faces from the captured image
        faces_captured_resized = []
        for (x, y, w, h) in faces_captured:
            faces_captured_resized.append(cv2.resize(captured_image_array[y:y+h, x:x+w], (92, 112)))

        # Get all the images from the database
        db_images = UserProfile.objects.all()

        # Initialize a list to store the similarity scores
        similarity_scores = []

        # Loop through all the images in the database
        for db_image in db_images:
            # Perform face detection on the database image
            db_image_array = np.array(cv2.imread(db_image.profile_picture.path))
            faces_db = face_cascade.detectMultiScale(db_image_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces_db) == 0:
                continue

            # Resize and crop the detected faces from the database image
            faces_db_resized = []
            for (x, y, w, h) in faces_db:
                faces_db_resized.append(cv2.resize(db_image_array[y:y+h, x:x+w], (92, 112)))

            # Compute similarity scores for each pair of faces
            for face_captured in faces_captured_resized:
                for face_db in faces_db_resized:
                    similarity_score = cv2.compareHist(cv2.calcHist([face_captured], [0], None, [64], [0, 100]),
                                                      cv2.calcHist([face_db], [0], None, [64], [0, 100]),
                                                      cv2.HISTCMP_CORREL) * 100

                    similarity_scores.append(similarity_score)

        # Get the index of the most similar face in the database
        most_similar_index = np.argmax(similarity_scores)

        # Calculate the match percentage
        num_faces_db = len(faces_db_resized)
        match_percentage = similarity_scores[most_similar_index] / 100
        most_similar_face_index = int(most_similar_index // num_faces_db)

        if most_similar_face_index < len(db_images):
            print({'user': db_images[most_similar_face_index], 'identified_user': db_images[most_similar_face_index].user, 'match_percentage': match_percentage})
            # Return the most similar face and the user information
            return render(request, 'compare_result.html', {'user': db_images[most_similar_face_index], 'identified_user': db_images[most_similar_face_index].user, 'match_percentage': match_percentage})
        else:
            # Return an error message
            return render(request, 'does_not_exist.html', {'error_message': 'Index out of range'})
    else:
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