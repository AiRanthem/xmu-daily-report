FROM selenium/standalone-chrome:latest
WORKDIR /app
COPY . .
RUN sudo apt-get update && \
    sudo apt-get install -y --no-install-recommends python3-pip && \
    sudo rm -rf /var/lib/apt/lists/* && \
    pip3 install -r requirements.txt --no-cache-dir
CMD chmod +x XMUAutoCheckIn.sh && ./XMUAutoCheckIn.sh
