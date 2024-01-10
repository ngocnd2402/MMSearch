FROM python:3.8-alpine
COPY . .
WORKDIR /parseq

RUN apt install python3-pip
RUN pip install Pillow==9.0.0
RUN pip install torchtext==0.11.0
RUN pip install torchvision==0.11.3
RUN pip install pytorch-lightning
RUN pip install torch==1.10.2 -f https://download.pytorch.org/whl/torch_stable.html
RUN pip install -r /requirements.txt
RUN pip install -e .
CMD ["python3","./test_1_img.py"]
