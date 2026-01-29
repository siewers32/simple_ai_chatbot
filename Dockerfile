FROM python:trixie

RUN useradd -m appuser

# Stel de werkmap in
WORKDIR /home/appuser/app

USER appuser

COPY ./app/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

CMD [ "bash" ]