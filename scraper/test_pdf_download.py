import sqlite3
import requests
from bs4 import BeautifulSoup
import os

db = sqlite3.connect('bis_standards.db')
rows = db.execute("SELECT is_number, source_url FROM standards WHERE department_name='Ayush Department(AYD)' LIMIT 5").fetchall()

print("Testing 5 Standards for PDF Download...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

for is_number, url in rows:
    print(f"\n--- {is_number} ---")
    print(f"URL: {url}")
    try:
        res = requests.get(url, headers=headers, timeout=10)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        # Find download links
        download_links = soup.find_all('a', href=True)
        pdf_links = [a['href'] for a in download_links if 'pdf' in a['href'].lower() or 'download' in a['href'].lower() or 'BisProd' in a['href']]
        
        if not pdf_links:
            print("No obvious PDF download link found on page.")
        else:
            print(f"Found {len(pdf_links)} potential download links. Best guess: {pdf_links[0]}")
            dl_url = pdf_links[0]
            if dl_url.startswith('/'):
                dl_url = "https://standards.bis.gov.in" + dl_url
                
            print(f"Attempting to download: {dl_url}")
            pdf_res = requests.get(dl_url, headers=headers, timeout=10)
            
            # Check if it's a real PDF
            content_type = pdf_res.headers.get('Content-Type', '')
            content_disp = pdf_res.headers.get('Content-Disposition', '')
            
            print(f"Status Code: {pdf_res.status_code}")
            print(f"Content-Type: {content_type}")
            print(f"File Size: {len(pdf_res.content)} bytes")
            
            if 'pdf' in content_type.lower():
                print("SUCCESS: It's a real PDF!")
                with open(f"{is_number.replace(':', '_')}.pdf", 'wb') as f:
                    f.write(pdf_res.content)
            elif pdf_res.status_code == 200:
                print("Downloaded something, but it doesn't look like a direct PDF. Checking preview...")
                print(pdf_res.text[:200])
            else:
                print(f"Failed. Status: {pdf_res.status_code}")
                
    except Exception as e:
        print(f"Error fetching {is_number}: {e}")
