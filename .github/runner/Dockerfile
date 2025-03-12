FROM ubuntu:20.04

# Input GitHub runner version argument
ARG RUNNER_VERSION
ENV DEBIAN_FRONTEND=noninteractive
ENV USER=runner_user

LABEL Author="Pankaj Kumar Patel"
LABEL Email="pankajackson@live.co.uk"
LABEL GitHub="https://github.com/pankajackson"
LABEL BaseImage="ubuntu:20.04"
LABEL RunnerVersion=${RUNNER_VERSION}

# Update and install required packages
RUN apt-get update -y && apt-get upgrade -y && \
    apt-get install -y --no-install-recommends \
    curl nodejs wget unzip vim git azure-cli jq build-essential libssl-dev \
    libffi-dev python3 python3-venv python3-dev python3-pip docker.io && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user and add to the docker group
RUN useradd -m $USER && usermod -aG docker $USER

# Download and install GitHub Actions runner
RUN cd /home/$USER && mkdir actions-runner && cd actions-runner \
    && curl -O -L https://github.com/actions/runner/releases/download/v${RUNNER_VERSION}/actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz \
    && tar xzf ./actions-runner-linux-x64-${RUNNER_VERSION}.tar.gz

# Install additional dependencies
RUN chown -R $USER:$USER /home/$USER/actions-runner && /home/$USER/actions-runner/bin/installdependencies.sh

# Copy start script
ADD scripts/start.sh start.sh
RUN chmod +x start.sh


# Set the user to "$USER"
USER $USER
# WORKDIR /home/$USER/actions-runner

# Set the entrypoint to the start.sh script
ENTRYPOINT ["./start.sh"]
