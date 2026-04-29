#!/bin/bash

set -x

docker-compose up -d

docker exec -it namenode hdfs dfsadmin -safemode leave

docker exec -it namenode mkdir -p /data
docker exec -it namenode hadoop fs -mkdir -p /data

docker cp data/employee_data.csv namenode:/data/employee_data.csv
docker cp data/currency_rates.json namenode:/data/currency_rates.json
docker exec -it namenode hadoop fs -put -f /data/employee_data.csv hdfs://namenode:9000/data/employee_data.csv
docker exec -it namenode hadoop fs -put -f /data/currency_rates.json hdfs://namenode:9000/data/currency_rates.json


docker exec spark-master mkdir -p jobs
docker cp spark_job.py spark-master:/jobs/spark_job.py
docker exec -it spark-master /spark/bin/spark-submit \
  --master spark://spark-master:7077 \
  /jobs/spark_job.py

docker cp data/create_employee_table.sql hive-server:/data/create_employee_table.sql

docker exec -it hive-server hive -f /data/create_employee_table.sql

num_rows=$(docker exec -it hive-server beeline -u "jdbc:hive2://localhost:10000/default" -e "SELECT COUNT(*) as number_of_rows FROM employee_salary;")

echo "$num_rows"



