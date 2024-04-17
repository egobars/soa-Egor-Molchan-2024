FROM python
WORKDIR /posts_service
COPY /src/requirements.txt /posts_service/requirements.txt
RUN pip3 install --no-cache-dir -r /posts_service/requirements.txt
COPY /src /posts_service/src
COPY /migrations /posts_service/migrations
COPY /proto /posts_service/proto
COPY /entrypoint.sh /posts_service/
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]