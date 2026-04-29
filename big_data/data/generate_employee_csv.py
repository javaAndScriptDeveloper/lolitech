import csv
import random

output_csv_path = 'employee_data.csv'

num_records = 1000000
currencies = ["USD", "EUR", "CAD"]

with open(output_csv_path, mode='w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)

    csv_writer.writerow(['employee_id', 'salary'])

    for _ in range(num_records):
        employee_id = random.randint(0, 1000)
        salary = random.randint(0, 1000)
        currency = random.choice(currencies)
        csv_writer.writerow([employee_id, salary, currency])

print(f"CSV file generated at: {output_csv_path}")