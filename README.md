# CMPE 273 – Week 1 Lab 1: First Distributed System

Two HTTP services that communicate over the network: **Service A** (Echo API) and **Service B** (Client). Service B calls Service A with a timeout; when Service A is down, Service B returns HTTP 503 and logs the error.

<img width="1148" height="173" alt="42-44 164449 (D0P9  servicenservice-s endpeistaesilecte statusserres" src="https://github.com/user-attachments/assets/807fe52e-1338-4e4a-a776-69a1b6c61c1b" />


<img width="589" height="183" alt="• ekantkapgate@Ekants-MacBook-Air service-b  python3 app-py" src="https://github.com/user-attachments/assets/5085795d-e1d6-41be-a1f0-0c0f3b440108" />


<img width="859" height="178" alt="Pasted Graphic 3" src="https://github.com/user-attachments/assets/be11876f-40b1-42e4-a6a5-2abd9d60b322" />

## How to Run Locally

**Prerequisites:** Python 3.10+, Git (no external dependencies)

### 1. Run Service A (Echo API)

```bash
cd cmpe273-week1-lab1/service-a
python app.py
```

Leave this terminal running. You should see a startup log line indicating host and port.

### 2. Run Service B (Client) — in a **second** terminal

```bash
cd cmpe273-week1-lab1/service-b
python app.py
```

You should see a startup log line indicating host and port.

### 3. Test

**Success (both services up):**

```bash
curl "http://127.0.0.1:8081/call-echo?msg=hello"
```

Expected: `{"service_b":"ok","service_a":{"echo":"hello"}}` and HTTP 200. Service B logs something like: `service=service-b endpoint=/call-echo status=ok latency_ms=...`

**Failure (Service A stopped):**

1. Stop Service A (Ctrl+C in its terminal).
2. Run the same curl again:

```bash
curl -i "http://127.0.0.1:8081/call-echo?msg=hello"
```

Expected: HTTP **503** and a JSON body with `service_a: "unavailable"` and an `error` message. Service B logs an **error** line, e.g. `status=error error="connection refused ..."`.

## Success + Failure Proof

### Success (both services running)

```text
$ curl "http://127.0.0.1:8081/call-echo?msg=hello"
{"service_b":"ok","service_a":{"echo":"hello"}}
```

Service B log example:

```text
2025-02-04 12:00:00 [INFO] service=service-b endpoint=/call-echo status=ok latency_ms=5
```

### Failure (Service A stopped)

```text
$ curl -i "http://127.0.0.1:8081/call-echo?msg=hello"
HTTP/1.1 503 SERVICE UNAVAILABLE
...
{"error":"Service A unreachable (connection refused or down)","service_a":"unavailable","service_b":"ok"}
```

Service B log example:

```text
2025-02-04 12:01:00 [ERROR] service=service-b endpoint=/call-echo status=error error="connection refused ..." latency_ms=1
```

*(Paste your actual `curl` output and log lines here or add a screenshot for submission.)*

## What Makes This Distributed?

This setup is **distributed** because **two separate processes** (Service A and Service B) run independently and communicate **over the network** (HTTP on localhost). Each service can fail on its own: if you stop Service A, Service B keeps running but correctly reports failure (503) when it cannot reach A. There is no shared memory—only messages over the wire—and the client (Service B) uses a **timeout** so it does not hang forever when the provider (Service A) is slow or down. That independence of processes and failure, plus network-based communication and timeout handling, are the core traits of a small distributed system.

## Reference

Starter repo (used as reference; this is an independent implementation):  
https://github.com/ranjanr/cmpe273-week1-lab1-starter
