FROM python:3.14-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# app.py and test_inventory.py come from the team's Week 3/4 build;
# crm_copilot.py is the Week 5 addition.
COPY app.py test_inventory.py crm_copilot.py test_crm_copilot.py ./
# Scanner library is served by the app itself, so a phone does not depend on a
# CDN being reachable during a demo (Week 4 decision P3).
COPY static/ ./static/

VOLUME /data

EXPOSE 5000

CMD ["python", "app.py"]
