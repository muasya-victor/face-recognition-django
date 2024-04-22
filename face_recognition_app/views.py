from django.shortcuts import render
from django.http import JsonResponse
from .models import CustomUser
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
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


def get_custom_user_by_username(username):
    User = get_user_model()
    try:
        user = User.objects.get(username=username)
        return user
    except User.DoesNotExist:
        return None

def identified_user(request, user_id):
    user = get_object_or_404(CustomUser, id=user_id)
    context = {
        'user': user
    }
    return render(request, 'identified_user.html', context)



def compare_image(request):
    print('captured image', request.FILES)

    match_results = {
        'user_id': None,
        'match_percentage': None,
        'captured_image_url': None,
        'status': None,
        'user': None
    }

    if request.method == 'POST':
        captured_image = request.FILES.get('captured_image')

        captured_image_array = cv2.imdecode(np.frombuffer(captured_image.read(), np.uint8), -1)

        if captured_image_array is None:
            return JsonResponse({'status': 'error', 'message': 'Invalid image'})

        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        faces_captured = face_cascade.detectMultiScale(captured_image_array, scaleFactor=1.2, minNeighbors=5, minSize=(20, 20))

        if len(faces_captured) == 0:
            return JsonResponse({'status': 'error', 'message': 'No face detected'})

        faces_captured_resized = [cv2.resize(captured_image_array[y:y+h, x:x+w], (92, 112)) for (x, y, w, h) in faces_captured]

        db_images = CustomUser.objects.all()

        similarity_scores = []

        for db_image in db_images:
            db_image_array = cv2.imread(db_image.user_avatar.path)

            if db_image_array is None:
                continue

            faces_db = face_cascade.detectMultiScale(db_image_array, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

            if len(faces_db) == 0:
                continue

            faces_db_resized = [cv2.resize(db_image_array[y:y+h, x:x+w], (92, 112)) for (x, y, w, h) in faces_db]

            for face_captured in faces_captured_resized:
                for face_db in faces_db_resized:
                    similarity_score = cv2.compareHist(cv2.calcHist([face_captured], [0], None, [64], [0, 100]),
                                                      cv2.calcHist([face_db], [0], None, [64], [0, 100]),
                                                      cv2.HISTCMP_CORREL)
                    similarity_scores.append(similarity_score)

        if not similarity_scores:
            match_results['status'] = 'error'
        else:
            match_results['status'] = 'success'

            most_similar_index = np.argmax(similarity_scores)
            num_faces_db = len(faces_db_resized)
            match_results['match_percentage'] = similarity_scores[most_similar_index] * 100
            most_similar_face_index = int(most_similar_index // num_faces_db)

            if most_similar_face_index < len(db_images):
                user_id = db_images[most_similar_face_index].id
                identified_user = CustomUser.objects.get(id=user_id)
                match_results['user'] = {
                    'id': identified_user.id,
                    'username': identified_user.username,
                    }
                match_results['user_id'] = user_id


                _, encoded_image = cv2.imencode('.jpg', captured_image_array)
                recognition_history = RecognitionHistory.objects.create(
                                        recognition_image=ContentFile(encoded_image.tobytes(), name=captured_image.name),
                                        user=identified_user
                                    )

                match_results['captured_image_url'] = recognition_history.recognition_image.url

        # For debugging
        print(match_results)

        return JsonResponse(match_results)

    else:
        return render(request, 'compare_image.html')



def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('admin_report')  # Redirect to the desired page after login
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

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle

def generate_pdf_report(request):
    # Fetch recognition history data
    recognition_history = RecognitionHistory.objects.all()

    # Create a response object
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="recognition_report.pdf"'

    # Create a PDF object
    pdf = SimpleDocTemplate(response, pagesize=A4)
    
    # Set font and size
    styles = getSampleStyleSheet()
    styleN = styles['BodyText']
    styleN.alignment = 1

    # Create table data
    data = [["Recognition Time", "User"]]
    for history in recognition_history:
        data.append([str(history.recogntion_time), str(history.user.username)])

    # Create table
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    # Add table to PDF
    elements = []
    elements.append(table)

    # Generate PDF
    pdf.build(elements)

    return response


def login_history_view(request):
    # Fetch all RecognitionHistory objects
    history_entries = RecognitionHistory.objects.all()

    # Pass history_entries to the template
    context = {
        'history_entries': history_entries
    }

    return render(request, 'admin.html', context)