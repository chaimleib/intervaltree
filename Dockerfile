# Modified by chaimleib March 2023 from
#   https://github.com/vicamo/docker-pyenv/blob/main/alpine/Dockerfile
#
# Changes:
# * customize the versions of python installed
# * remove the dependency on github.com/momo-lab/xxenv-latest
# * forbid failures when building python
# * add other tools like parallel
# * run intervaltree tests

FROM alpine:latest AS base

ENV PYENV_ROOT="/opt/pyenv"
ENV PYENV_SHELL="bash"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:$PATH"

# http://bugs.python.org/issue19846
# > At the moment, setting "LANG=C" on a Linux system *fundamentally breaks Python 3*, and that's not OK.
ENV LANG C.UTF-8

# runtime dependencies
RUN set -eux; \
    apk update; \
    apk add --no-cache \
        bash \
        build-base \
        bzip2 \
        ca-certificates \
        curl \
        expat \
        git \
        libffi \
        mpdecimal \
        ncurses-libs \
        openssl \
        parallel \
        readline \
        sqlite-libs \
        tk \
        xz \
        zlib \
    ;

RUN set -eux; \
    curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash; \
    pyenv update

FROM base AS builder

# runtime dependencies
RUN set -eux; \
    apk update; \
    apk add --no-cache \
        bzip2-dev \
        libffi-dev \
        ncurses-dev \
        openssl-dev \
        readline-dev \
        sqlite-dev \
        tk-dev \
        xz-dev \
        zlib-dev \
    ;

FROM builder AS build-2.7.18
RUN set -eux; pyenv install 2.7.18; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.6.15
RUN set -eux; pyenv install 3.6.15; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.7.16
RUN set -eux; pyenv install 3.7.16; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.8.16
RUN set -eux; pyenv install 3.8.16; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.9.16
RUN set -eux; pyenv install 3.9.16; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.10.10
RUN set -eux; pyenv install 3.10.10; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM builder AS build-3.11.2
RUN set -eux; pyenv install 3.11.2; \
  find ${PYENV_ROOT}/versions -depth \
        \( \
            \( -type d -a \( -name test -o -name tests -o -name idle_test \) \) \
            -o \( -type f -a -name 'wininst-*.exe' \) \
        \) -exec rm -rf '{}' +

FROM base AS tester
COPY --from=build-2.7.18 /opt/pyenv/versions/2.7.18 /opt/pyenv/versions/2.7.18
COPY --from=build-3.6.15 /opt/pyenv/versions/3.6.15 /opt/pyenv/versions/3.6.15
COPY --from=build-3.7.16 /opt/pyenv/versions/3.7.16 /opt/pyenv/versions/3.7.16
COPY --from=build-3.8.16 /opt/pyenv/versions/3.8.16 /opt/pyenv/versions/3.8.16
COPY --from=build-3.9.16 /opt/pyenv/versions/3.9.16 /opt/pyenv/versions/3.9.16
COPY --from=build-3.10.10 /opt/pyenv/versions/3.10.10 /opt/pyenv/versions/3.10.10
COPY --from=build-3.11.2 /opt/pyenv/versions/3.11.2 /opt/pyenv/versions/3.11.2

RUN set -eux; \
    pyenv rehash; \
    pyenv versions

WORKDIR /intervaltree
COPY . .
CMD [ "scripts/testall.sh" ]

