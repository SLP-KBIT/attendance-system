FROM python

RUN apt update 
RUN apt install -y openssh-client pip

WORKDIR /app
COPY ./app /app

RUN mkdir ./key
RUN ssh-keygen -q -t rsa -N '' -f ./key/attendance_key

RUN mkdir ./data

RUN pip install flask sqlalchemy

CMD ["python", "main.py"]