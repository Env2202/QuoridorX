FROM swe-arena-base

RUN apt-get update && apt-get install -y \
    git \
    python3-pip \
    python3-virtualenv \
    python3-venv \
    libglib2.0-0 \
    libsm6 \
    libice6 \
    libgl1 \
    libegl1 \
    libdbus-1-3 \
    libfontconfig1 \
    libopengl0 \
    libxrender1 \
    libxext6 \
    libxi6 \
    libx11-xcb1 \
    libxkbcommon-x11-0 \
    libxcb-cursor0 \
    libxcb-icccm4 \
    libxcb-image0 \
    libxcb-keysyms1 \
    libxcb-randr0 \
    libxcb-render-util0 \
    libxcb-shape0 \
    libxcb-xinerama0 \
    libxcb-xfixes0 \
    --no-install-recommends && rm -rf /var/lib/apt/lists/*

ENV COMMIT_HASH=b150a73ed24cce9f114d047cc3791d55cf304d51
ENV REPO_URL=https://github.com/Env2202/QuoridorX.git
ENV REPO_NAME=QuoridorX
ENV VENV_PATH=/opt/venv
ENV PATH="${VENV_PATH}/bin:${PATH}"

WORKDIR /testbed/${REPO_NAME}

RUN git init && \
    git remote add origin ${REPO_URL} && \
    git fetch --depth 1 origin ${COMMIT_HASH} && \
    git checkout FETCH_HEAD && \
    git remote remove origin

RUN python3 -m venv ${VENV_PATH} && \
    pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt && \
    if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt; fi

# Useful defaults for local GUI + analysis runs in containerized environments.
ENV QT_X11_NO_MITSHM=1
ENV PYTHONUNBUFFERED=1

# Default command runs the game app.
CMD ["python", "src/app.py"]
