# BTRrepo

This project provides a tool for refining Hyperledger Fabric transaction data into an analyzable format.
It parses transaction logs and extracts structured JSON with 4W1H pattern.
Useful for business flow analysis or audit log preprocessing.


## Prerequisites

- [Hyperledger Fabric v2.5](https://hyperledger-fabric.readthedocs.io/en/release-2.5/)
- Python 3.x
- Docker & Docker Compose
- `docker-elk.zip` (ELK stack configuration)

---

## Installation

### 1. Install Hyperledger Fabric v2.5
Follow the official [Fabric documentation](https://hyperledger-fabric.readthedocs.io/en/release-2.5/)  
to set up the Fabric binaries and samples.

### 2. Install Python packages
```bash
pip install -r requirements.txt
```
### 3. Setup ELK Stack
Unzip the provided ELK package and start the containers:


```bash
unzip docker-elk.zip
cd docker-elk
docker-compose up -d
```

### 4. Smart Contract Deployment
Smart contracts are deployed using instructions from here[https://github.com/okcdbu/FabricSCMS]

### Usage
1. Run blockchain transactions through deployed smart contracts.

2. Generated transaction logs will be stored in Elasticsearch (via ELK stack configuration).

3. Visualize the transaction data:
```bash
python visualizer.py
```

4. Access transaction dashboards using Kibana (http://localhost:5601 by default).

Notes
- Ensure Docker has enough memory allocated (recommended: 4GB+).
- Elasticsearch and Kibana may take a few minutes to initialize.
- Modify docker-elk configurations if you need custom index names or mappings.
