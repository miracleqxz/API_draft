FROM python:3.12
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "from tensorflow.keras.applications import InceptionV3; InceptionV3(weights='imagenet')"
COPY . .
CMD ["python", "app.py"]