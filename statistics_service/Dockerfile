FROM python
WORKDIR /statistics_service
COPY /src/requirements.txt /statistics_service/requirements.txt
RUN pip3 install --no-cache-dir -r /statistics_service/requirements.txt
COPY /src /statistics_service/src
COPY /proto /statistics_service/proto
COPY /entrypoint.sh /statistics_service
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]