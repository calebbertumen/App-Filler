import csv
from pathlib import Path

def csv_to_dict(filename):
    with open(filename, 'r') as csvfile:
        reader = csv.DictReader(csvfile)
        return list(reader)

base_path = Path(__file__).parent.resolve()
filename = base_path / "Client Info" / "TestCSV - VB.csv"
clients = csv_to_dict(str(filename)) # Dict of individual client's info

client = clients[3]  
username = client['Email']
password = 'Password123!'
# sensitive_data = {'x_username': username, 'x_password': password,} # The LLM will only see placeholder names, never the actual values


if __name__ == '__main__':
    print(client)