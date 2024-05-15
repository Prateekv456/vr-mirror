from flask import Flask, request, jsonify
import os

app = Flask(__name__)

# Endpoint to receive image data and process it
@app.route('/api/endpoint', methods=['POST'])
def customize_tshirt():
    # Receive image data from the request
    image_data = request.json.get('imageData')

    # Process the image data (replace this with your actual processing logic)
    # Here, we'll simply save the image to a folder named "uploads"
    if image_data:
        save_image(image_data)

    # Return a response indicating success
    return jsonify({'message': 'Image received and processed successfully'})

def save_image(image_data):
    # Create a directory to store uploaded images if it doesn't exist
    if not os.path.exists('uploads'):
        os.makedirs('uploads')

    # Generate a unique filename for the image
    image_filename = os.path.join('uploads', 'custom_tshirt.jpg')

    # Decode base64 image data and save it as a file
    with open(image_filename, 'wb') as f:
        f.write(image_data.decode('base64'))

if __name__ == '__main__':
    app.run(debug=True)
