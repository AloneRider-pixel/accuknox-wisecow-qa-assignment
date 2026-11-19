FROM debian:bookworm-slim
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       bash cowsay fortune-mod fortunes-min netcat-openbsd socat curl \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 wisecow \
    && useradd --uid 10001 --gid wisecow --no-create-home wisecow \
    && mkdir -p /run/wisecow /opt/wisecow \
    && chown wisecow:wisecow /run/wisecow
ENV PATH="/usr/games:${PATH}"
COPY --chmod=0555 wisecow.sh /opt/wisecow/wisecow.sh
COPY LICENSE /opt/wisecow/LICENSE
USER 10001:10001
WORKDIR /run/wisecow
EXPOSE 4499
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl --fail --max-time 4 --silent http://127.0.0.1:4499/ > /dev/null || exit 1
CMD ["bash", "/opt/wisecow/wisecow.sh"]
