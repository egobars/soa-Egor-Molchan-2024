FROM python
WORKDIR /main_service
COPY /src/requirements.txt /main_service/requirements.txt
RUN pip3 install --no-cache-dir -r /main_service/requirements.txt
COPY /src /main_service/
COPY /migrations /main_service/
COPY /entrypoint.sh /main_service/
RUN chmod +x entrypoint.sh
ENTRYPOINT ["./entrypoint.sh"]