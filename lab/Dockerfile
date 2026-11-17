FROM python:3.12-slim

WORKDIR /opt/loom

COPY src-v1.9.0/agents/adk_agent/requirements.txt /tmp/adk-requirements.txt
RUN pip install --no-cache-dir -r /tmp/adk-requirements.txt "strands-agents>=0.1.0"

COPY src-v1.9.0/agents /opt/loom/agents
COPY poc.py /lab/poc.py

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    AWS_EC2_METADATA_DISABLED=true \
    AWS_DEFAULT_REGION=us-east-1 \
    AWS_REGION=us-east-1 \
    AWS_ACCESS_KEY_ID=lab \
    AWS_SECRET_ACCESS_KEY=lab \
    LOOM_SRC_ROOT=/opt/loom \
    LAB_HOST=127.0.0.1 \
    LAB_PORT=18740

EXPOSE 18740
CMD ["sleep", "infinity"]
