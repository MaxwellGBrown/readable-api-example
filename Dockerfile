# -----------------------------------------------------------------------------
# Usage:
#   docker build --tag readable-api .
#   docker run -d -v $(pwd):/usr/src/app -p 8888:80 --name readable-api readable-api
# -----------------------------------------------------------------------------

FROM python:3.7

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app
ENV PYTHONPATH=/usr/src/app

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["gunicorn"]
CMD [ \
  "-b", "0.0.0.0:80", \
  "-w", "4", \
  "--access-logfile", "-", \
  "--access-logformat", "%(m)s %(U)s %(l)s %(s)s", \
  "--reload", \
  "readable_api:build_wsgi()" \
]

EXPOSE 80
