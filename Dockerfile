FROM python:3.9-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    libssl-dev \
    python3-dev \
    wget \
    curl \
    unzip \
    dbus-x11 \
    libgtk-3-0 \
    libasound2 \
    xvfb \
    xauth \
    libdbus-glib-1-2 \
    fonts-freefont-ttf \
    && wget -q "https://github.com/mozilla/geckodriver/releases/download/v0.35.0/geckodriver-v0.35.0-linux64.tar.gz" \
    && tar -xvzf geckodriver-v0.35.0-linux64.tar.gz \
    && mv geckodriver /usr/local/bin/ \
    && rm geckodriver-v0.35.0-linux64.tar.gz \
    && wget -q -O firefox.tar.bz2 "https://download.mozilla.org/?product=firefox-latest&os=linux64&lang=en-US" \
    && tar -xjf firefox.tar.bz2 \
    && mv firefox /usr/local/firefox \
    && ln -s /usr/local/firefox/firefox /usr/local/bin/firefox-bin \
    && rm firefox.tar.bz2 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

ENV PATH="/usr/local/firefox:$PATH"
ENV PATH="/usr/local/bin:$PATH"

ENV DISPLAY=:99

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["xvfb-run", "-s", "-screen 0 1920x1080x24", "python", "manage.py", "runserver", "0.0.0.0:8000"]
