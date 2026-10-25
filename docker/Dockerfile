FROM debian:latest

ARG TARGET_DIR="/opt/ut99"
ARG USER="server"
ARG UID="1000"
ARG GID="1000"
ARG INSTALLER_URL="https://raw.githubusercontent.com/OldUnreal/FullGameInstallers/master/Linux/install-ut99.sh"
ARG REDEEMOD_URL="https://github.com/domasles/redeemod/releases/latest/download/redeemod-cli-linux"

ENV DEBIAN_FRONTEND=noninteractive

RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        wget \
        bash \
        curl \
        python3 \
        ca-certificates \
        libstdc++6:i386 \
        zlib1g:i386 \
        libc6:i386 \
        p7zip-full \
        jq \
        lbzip2 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid ${GID} ${USER} && \
    useradd --uid ${UID} --gid ${GID} --create-home --home-dir ${TARGET_DIR} --shell /bin/bash ${USER}

USER ${USER}
WORKDIR ${TARGET_DIR}

ENV HOME=${TARGET_DIR}
ENV UT_HOME=${TARGET_DIR}
ENV UT_USER=${USER}
ENV PYTHONPATH=${UT_HOME}/docker
ENV REDEEMOD_CLI=${UT_HOME}/redeemod/redeemod-cli

RUN mkdir -p ${UT_HOME}/docker
RUN mkdir -p ${UT_HOME}/redeemod

RUN wget -q ${INSTALLER_URL} -O "./install-ut99.sh" && \
    chmod +x "./install-ut99.sh" && \
    echo "y" | "./install-ut99.sh" \
        --destination=${UT_HOME} \
        --ui-mode=auto \
        --application-entry=skip \
        --desktop-shortcut=skip \
        --no-unrealed \
        --no-keep-installer-files && \
    rm -f "./install-ut99.sh"

RUN wget -q ${REDEEMOD_URL} -O ${REDEEMOD_CLI} && \
    chmod +x ${REDEEMOD_CLI} && \
    ${REDEEMOD_CLI} add-game ut99 \
        --set-path executable_path=${UT_HOME}/System/ucc-bin \
        --set-path config_path=${UT_HOME}/System/UnrealTournament.ini

COPY --chown=${USER}:${USER} app/ ${UT_HOME}/docker/app/
COPY --chown=${USER}:${USER} docker/entrypoint.sh ${UT_HOME}/docker/entrypoint.sh

RUN chmod +x ${UT_HOME}/docker/entrypoint.sh

USER root

EXPOSE 7777/udp 7778/udp 7779/udp 7780/udp 7781/udp 8777/udp 8080/tcp

ENTRYPOINT ["/bin/bash", "-c", "exec \"$UT_HOME/docker/entrypoint.sh\""]
