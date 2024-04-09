import cv2
import numpy as np
from django.shortcuts import render
from .models import UserProfile

def compare_image(request):
    if request.method == 'POST':
        # Get the captured image from the request
        captured_image = request.FILES['captured_image']

        # Convert the captured image to a numpy array
        captured_image_array = np.array(cv2.imread(captured_image))

        # Get all the images from the database
        db_images = UserProfile.objects.all()

        # Initialize a list to store the similarity scores
        similarity_scores = []

        # Loop through all the images in the database
        for db_image in db_images:
            # Convert the database image to a numpy array
            db_image_array = np.array(cv2.imread(db_image.profile_picture))

            # Calculate the similarity score between the captured image and the database image
            similarity_score = cv2.compareHist(cv2.calcHist([captured_image_array], [0], None, [64], [0, 256]),
                                              cv2.calcHist([db_image_array], [0], None, [64], [0, 256]),
                                              cv2.HISTCMP_CORREL)

            # Append the similarity score to the list
            similarity_scores.append(similarity_score)

        # Get the index of the most similar image in the database
        most_similar_index = np.argmax(similarity_scores)

        # Get the most similar image from the database
        most_similar_image = db_images[most_similar_index]

        # Return the most similar image to the user
        return render(request, 'compare_result.html', {'most_similar_image': most_similar_image})

    return render(request, 'compare_image.html')