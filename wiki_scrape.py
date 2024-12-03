import requests
from bs4 import BeautifulSoup
import pandas as pd

def scrape_wikipedia_table(url, table_class):
    # Fetch the web page
    response = requests.get(url)
    if response.status_code != 200:
        raise Exception(f"Failed to load page {url}")
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the table
    table = soup.find('table', {'class': table_class})
    if table is None:
        raise Exception(f"Failed to find table with class {table_class}")
    
    # Extract table headers
    headers = [header.text.strip() for header in table.find_all('th')]
    
    # Extract table rows
    rows = []
    for row in table.find_all('tr')[1:]:
        cells = row.find_all(['td', 'th'])
        row_data = [cell.text.strip() for cell in cells]
        rows.append(row_data)
    print(rows) 
    # Create a DataFrame
    df = pd.DataFrame(rows)
    return df

# Example usage
url = 'https://en.wikipedia.org/wiki/List_of_S%26P_400_companies'
table_class = 'wikitable sortable'  # Adjust based on the specific table class
df = scrape_wikipedia_table(url, table_class)

# Print the DataFrame
print(df)

# Save to CSV
df.to_csv('sp500_companies.csv', index=False)