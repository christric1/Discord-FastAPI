ARG PORT=443

FROM cypress/browsers:node-18.16.0-chrome-114.0.5735.133-1-ff-114.0.2-edge-114.0.1823.51-1

RUN apt-get install python3 -y

RUN echo $(python3 -m site --user-base)

COPY requirements.txt  .

ENV PATH /home/root/.local/bin:${PATH}

RUN  apt-get update && apt-get install -y python3-pip && pip install -r requirements.txt  

COPY . .

CMD uvicorn main:app --host 0.0.0.0 --port $PORT