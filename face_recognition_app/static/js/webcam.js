
function captureImage() {
    var video = document.getElementById('video');
    var canvas = document.getElementById('canvas');
    var context = canvas.getContext('2d');

    // Set canvas dimensions to match video stream
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;

    // Draw video frame onto canvas
    context.drawImage(video, 0, 0, canvas.width, canvas.height);

    // Show canvas and hide video
    video.style.display = 'none';
    canvas.style.display = 'block';

    // Show submit button
    document.getElementById('submit-btn').style.display = 'block';

    // Show captured image
    var imageDataUrl = canvas.toDataURL('image/png');
    var capturedImage = document.getElementById('captured-image');
    capturedImage.src = imageDataUrl;
    document.getElementById('captured-image-container').style.display = 'block';
}

function submitImage() {
    var csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;
 // Get CSRF token from the page's HTML
    var canvas = document.getElementById('canvas');
    var imageData = canvas.toDataURL('image/png');

    // Send captured image to server with CSRF token
    $.ajax({
        type: 'POST',
        url: '/compare-images/',
        data: {
            csrfmiddlewaretoken: csrfToken, // Include CSRF token in data
            image_data: imageData
        },
        success: function(response) {
            // Display result message
            $('#result').html(response.message);
            console.log(imageData, 'image data');

        },
        error: function(xhr, status, error) {
            console.error(error);
            console.log(imageData, 'image data');

        }
    });
}

