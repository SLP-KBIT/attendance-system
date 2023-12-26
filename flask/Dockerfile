FROM python

RUN apt update 
RUN apt install -y openssh-client pip

WORKDIR /app
COPY ./app /app

# WORKDIR /app/key

# RUN ssh-keygen -q -t rsa -N '' -f id_rsa

# WORKDIR /app

RUN pip install flask sqlalchemy

CMD ["python", "main.py"]
