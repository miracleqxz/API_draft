FROM python:3.12
WORKDIR /usr/src/app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
RUN pip install ./en_core_web_sm-3.8.0.tar.gz
CMD ["python", "app.py"]