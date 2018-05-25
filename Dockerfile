FROM python:3.6-alpine
RUN pip install requests elasticsearch
COPY index.py /index.py
CMD ["python3", "/index.py"]