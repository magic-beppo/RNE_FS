import faostat
import pandas as pd
import time

# (Optional) set a timeout so it won't hang indefinitely
faostat.set_requests_args(timeout=30)

# Your list of M49 area codes
area_codes = [59, 103, 112, 121, 212, 276, 5305, 5000, 5308, 5103, 5100, 5300]

# Try with a smaller subset first to test
test_codes = area_codes[:3]  # Just first 3 for testing

try:
    # Option 1: Try with a different parameter format
    df = faostat.get_data(
        "FS",
        pars={"geographicAreaM49": ",".join(map(str, test_codes))},  # Comma-separated string
        show_flags=False
    )
    
    # If that works, proceed with all codes
    if not df.empty:
        df = faostat.get_data(
            "FS",
            pars={"geographicAreaM49": ",".join(map(str, area_codes))},
            show_flags=False
        )
        
except Exception as e:
    print(f"First approach failed: {e}")
    try:
        # Option 2: Try fetching data in smaller batches
        dfs = []
        for code in area_codes:
            print(f"Fetching data for area code: {code}")
            temp_df = faostat.get_data(
                "FS",
                pars={"geographicAreaM49": str(code)},
                show_flags=False
            )
            dfs.append(temp_df)
            time.sleep(1)  # Add delay to avoid overwhelming the server
            
        df = pd.concat(dfs, ignore_index=True)
    except Exception as e:
        print(f"Second approach failed: {e}")
        raise

# If we have data, proceed with processing
if not df.empty:
    # Rename to your internal schema
    df.rename(columns={
        "geographicAreaM49": "Area Code",
        "geographicArea":    "Area",
        "itemM49":           "Item Code",
        "item":              "Item",
        "elementM49":        "Element Code",
        "element":           "Element",
        "timePointYears":    "Year",
        "Value":             "Value",
        "Flag":              "Flag"
    }, inplace=True)

    # Convert types & normalize year
    df["Value"] = pd.to_numeric(df["Value"], errors="coerce")
    df["Year"]  = df["Year"].astype(int)

    print(df.head())
else:
    print("No data was retrieved. Please check your parameters.")