FROM ubuntu:22.04

ARG TARGET_DIR="/opt/ut99"
ARG USER="server"
ARG UID="1000"
ARG GID="1000"
ARG INSTALLER_URL="https://raw.githubusercontent.com/OldUnreal/FullGameInstallers/master/Linux/install-ut99.sh"

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
        libncurses5:i386 \
        p7zip-full \
        jq \
        lbzip2 && \
    rm -rf /var/lib/apt/lists/*

RUN groupadd --gid "${GID}" "${USER}" && \
    useradd --uid "${UID}" --gid "${GID}" --create-home --home-dir "${TARGET_DIR}" --shell /bin/bash "${USER}"

USER ${USER}
WORKDIR ${TARGET_DIR}

ENV HOME=${TARGET_DIR}
ENV UT_HOME=${TARGET_DIR}
ENV UT_USER=${USER}
ENV PYTHONPATH=${TARGET_DIR}

RUN wget -q "${INSTALLER_URL}" -O ./install-ut99.sh && \
    chmod +x ./install-ut99.sh && \
    echo "y" | ./install-ut99.sh \
        --destination=${TARGET_DIR} \
        --ui-mode=auto \
        --application-entry=skip \
        --desktop-shortcut=skip \
        --no-unrealed \
        --no-keep-installer-files && \
    rm -f ./install-ut99.sh

COPY --chown=${USER}:${USER} app/ ${TARGET_DIR}/app/
COPY --chown=${USER}:${USER} docker/entrypoint.sh ${TARGET_DIR}/entrypoint.sh

RUN chmod +x ${TARGET_DIR}/entrypoint.sh

USER root

EXPOSE 7777/udp 7778/udp 7779/udp 7780/udp 7781/udp 8777/udp 8080/tcp

ENTRYPOINT ["/bin/bash", "-c", "exec \"$UT_HOME/entrypoint.sh\""]
