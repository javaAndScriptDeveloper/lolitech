from pyspark.sql import SparkSession

def main():
    # Initialize Spark
    spark = SparkSession.builder.appName("AverageSalary").getOrCreate()

    # Read data from CSV file
    data = spark.read.csv('hdfs://namenode:9000/data/employee_data.csv', header=True, inferSchema=True)

    # Read currency conversion rates from JSON file on HDFS
    currency_rates = spark.read.json('hdfs://namenode:9000/data/currency_rates.json')

    # Collect currency conversion rates as a dictionary
    currency_dict = dict(currency_rates.rdd.map(lambda row: (row['currency'], row['conversion_rate'])).collect())

    # Broadcast the currency conversion rates to all worker nodes
    currency_broadcast = spark.sparkContext.broadcast(currency_dict)

    # Map data to key-value pairs (employee_id, (salary, currency))
    employee_salaries = data.rdd.map(lambda row: (row['employee_id'], (row['salary'], row['currency'])))

    # First MapReduce stage: Calculate sum and count for each employee
    sum_count = employee_salaries.groupByKey().mapValues(lambda values: (sum(v[0] for v in values), len(values)))

    # Second MapReduce stage: Calculate average salary and convert to base currency
    def convert_and_average(row):
        employee_id, (total_salary, count) = row
        average_salary = total_salary / count
        currency = employee_salaries.lookup(employee_id)[0][1]
        conversion_rate = currency_broadcast.value.get(currency, 1.0)
        converted_salary = average_salary * conversion_rate
        return (employee_id, converted_salary)

    average_salaries = sum_count.map(convert_and_average)

    # Save the result as a CSV file in HDFS
    average_salaries.toDF(['employee_id', 'avg_salary']).write.mode('overwrite').csv('hdfs://namenode:9000/data/result.csv', header=True)

    # Stop Spark
    spark.stop()

if __name__ == "__main__":
    main()
