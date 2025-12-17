"""
DIAGNOSTIC SCRIPT - Run this locally to understand the year issue
Add this to the TOP of your Display_module_1.py after loading the CSV
"""

import pandas as pd

# After these lines:
# df = pd.read_csv(PathData, encoding='ISO-8859-1', dtype={'Item Code': str})
# df['Value'] = pd.to_numeric(df['Value'], errors='coerce')
# ... year transformation code ...

print("=" * 80)
print("DIAGNOSTIC: Year Mismatch Analysis")
print("=" * 80)

# Check the three indicators used in scatter plot defaults
indicators_to_check = [
    'Prevalence of undernourishment (percent) (3-year average)',
    'Average dietary energy supply adequacy (percent) (3-year average)',
    'Gross domestic product per capita, PPP, (constant 2017 international $)'
]

for indicator in indicators_to_check:
    df_ind = df[df['Item'] == indicator]
    if not df_ind.empty:
        print(f"\n📊 {indicator[:50]}...")
        print(f"   Original Years: {sorted(df_ind['Year_Original'].unique())[:10]}")
        print(f"   Transformed Years: {sorted(df_ind['Year'].unique())[:10]}")
        print(f"   Total data points: {len(df_ind)}")
    else:
        print(f"\n❌ {indicator[:50]}... NOT FOUND IN DATA!")

# Check if selected years have data for ALL three indicators
selected_years = [2003, 2007, 2008, 2009, 2019, 2022]
print(f"\n\n🎯 Checking selected years: {selected_years}")

for year in selected_years:
    print(f"\n  Year {year}:")
    for indicator in indicators_to_check:
        df_check = df[(df['Year'] == year) & (df['Item'] == indicator)]
        if not df_check.empty:
            original = df_check['Year_Original'].iloc[0]
            print(f"    ✓ {indicator[:40]}: {original}")
        else:
            print(f"    ✗ {indicator[:40]}: NO DATA")

print("\n" + "=" * 80)
print("RECOMMENDATION:")
print("If you see '✗ NO DATA' for any indicator/year combination,")
print("that's why the scatter plot is empty!")
print("=" * 80)