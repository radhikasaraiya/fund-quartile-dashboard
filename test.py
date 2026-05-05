import requests

url = "https://research-ftp.bajajcapitalinsurance.com/Fund-Barometer.xls"
import os
filename = os.path.join("Data", "Fund-Barometer.xls")

try:
    print(f"Downloading {filename} from {url}...")
    # Adding headers to mimic a browser request, as some servers block basic scripts
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, stream=True, headers=headers)
    response.raise_for_status()  # Check if the request was successful
    
    with open(filename, 'wb') as file:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                file.write(chunk)
                
    print(f"Successfully downloaded {filename}")
except requests.exceptions.RequestException as e:
    print(f"Failed to download the file. Error: {e}")
