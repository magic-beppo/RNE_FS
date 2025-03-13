import pandas as pd

# Load the CSV file
df = pd.read_csv('FS_selection.csv', encoding='ISO-8859-1', dtype={'Item Code': str})

# Ensure 'Value' column is numeric
df['Value'] = pd.to_numeric(df['Value'], errors='coerce')

# Print unique values in 'Item' and 'Element' columns
print("Unique values in 'Item' column:\n", df['Item'].unique())
print("\nUnique values in 'Element' column:\n", df['Element'].unique())

# Filter data for a specific indicator with 'annual value'
indicator = "Prevalence of moderate or severe food insecurity in the rural adult population (percent) (annual value)"
df_filtered = df[df['Item'] == indicator]
print(f"\nFiltered data for {indicator}:\n", df_filtered)
