FROM hub.dataloop.ai/dtlpy-runner-images/cpu:python3.10_opencv
USER 1000
ENV HOME=/tmp
RUN pip install --user  \
    dtlpy \
    google-genai

# docker build -t gcr.io/viewo-g/piper/agent/runner/apps/google-gemini:0.0.2 -f ./Dockerfile  .
# docker run -it gcr.io/viewo-g/piper/agent/runner/apps/google-gemini:0.0.2 bash
# docker push gcr.io/viewo-g/piper/agent/runner/apps/google-gemini:0.0.2