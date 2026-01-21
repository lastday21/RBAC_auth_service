FROM ubuntu:latest
LABEL authors="NewUser"

ENTRYPOINT ["top", "-b"]