FROM docker.io/dataloopai/dtlpy-agent:cpu.py3.10.opencv
USER 1000
ENV HOME=/tmp
RUN pip install --user  \
    dtlpy \
    google-genai
