# AI-Based Fake Currency Detection using CNN and Image Processing

## Project Overview

The AI-Based Fake Currency Detection System is a deep learning and computer vision project designed to classify Indian currency note images as **Real** or **Fake**. It uses a trained EfficientNet-B3 model, image preprocessing, and a Flask-based web application to demonstrate automated currency image classification.

The project aims to explore how Artificial Intelligence (AI), Convolutional Neural Networks (CNN), and Image Processing can be applied to currency image analysis.

## Objectives

- Develop a deep learning-based currency image classification system.
- Apply image preprocessing techniques to prepare currency images for prediction.
- Integrate the trained model with a Flask web application.
- Display prediction results and model confidence scores.
- Maintain prediction history using a database.

## Key Features

- Upload currency note images for analysis.
- Predict whether an image is classified as Real or Fake.
- Display model prediction confidence.
- Provide a user-friendly web interface.
- Maintain prediction history using SQLite.
- Include an admin interface for relevant record management.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Core programming language |
| PyTorch | Deep learning framework |
| EfficientNet-B3 | Trained image classification model |
| CNN | Deep learning approach for image classification |
| OpenCV | Image processing |
| Pillow | Image loading and manipulation |
| Flask | Backend web framework |
| HTML and CSS | Web page structure and styling |
| JavaScript | Frontend interactivity |
| SQLite | Database for prediction history |

## System Workflow

1. The user uploads a currency note image.
2. The application validates and preprocesses the image.
3. The processed image is passed to the trained deep learning model.
4. The model generates a prediction.
5. The application displays the predicted class and confidence score.
6. The prediction can be stored in the history database.

## Project Structure

The project may contain the following components, depending on the implementation:

- `app.py` — Flask application entry point
- `templates/` — HTML templates
- `static/` — CSS, JavaScript, and static assets
- `models/` — Trained model files
- `database/` — Database-related files
- `requirements.txt` — Python dependencies

## Installation and Execution

1. Clone this repository.
2. Create and activate a Python virtual environment.
3. Install the required dependencies using `requirements.txt`.
4. Configure the trained model path and any required application settings.
5. Run the Flask application using `python app.py`.
6. Open the local URL displayed in the terminal in your browser.

Detailed setup instructions and dependencies will be updated to match the final project implementation.

## Disclaimer

This project is developed for academic and educational purposes. Its predictions depend on the training data and model performance and should not be treated as official currency authentication or as a substitute for verification by an authorized financial institution.

## Author

MCA Student Project

## Project Status

Academic project — implementation and documentation may be updated as development progresses.
