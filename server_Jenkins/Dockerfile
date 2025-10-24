FROM jenkins/jenkins:lts

USER root

RUN apt-get update && apt-get install -y \
    sudo\
    mc\
    git \
    python3 \
    python3-pip \
    curl \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && rm -rf /var/lib/apt/lists/*

# Pre-install dependencies
RUN pip3 install --break-system-packages pandas opencv-python pyyaml tabulate

USER jenkins

RUN jenkins-plugin-cli --plugins \
    git \
    pipeline-model-definition \
    workflow-aggregator \
    blueocean