FROM python:3.11

ENV PYTHONUNBUFFERED=True

WORKDIR /app
COPY container-injection.c .

RUN gcc -c -Wall -fpic container-injection.c
RUN gcc -shared -o libcontainer-injection.so container-injection.o


CMD ["bash", "-c", "echo override this; exit 1"]
