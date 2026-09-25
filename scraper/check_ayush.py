"""Check AYUSH department data completeness"""
import json
import glob

# Find the latest dept list
files = glob.glob('raw_store/standards_portal/*dept_list_AYUSH*.json')
files.sort(key=lambda f: open(f).read()[:10], reverse=True)

# Use the largest file
largest = max(files, key=lambda f: len(open(f).read()))
print(f"Using: {largest}")

data = json.load(open(largest, 'r', encoding='utf-8'))
items = data.get('data', [])
total = data.get('totalRecord', len(items))
print(f"Total records in BIS AYUSH department: {total}")
print(f"Records in this file: {len(items)}")

# Show sample
print(f"\nSample standards (first 10):")
for s in items[:10]:
    print(f"  IS {s.get('standardNumber','?'):20s}: {s.get('standardTitle','?')[:90]}")

# Now check individual standard detail files
detail_files = glob.glob('raw_store/standards_portal/*standard_IS_*.json')
print(f"\nTotal individual standard detail files: {len(detail_files)}")

# Read one sample standard
if detail_files:
    sample = json.load(open(detail_files[0], 'r', encoding='utf-8'))
    print(f"\nSample standard detail structure (keys):")
    def show_keys(d, prefix="  "):
        if isinstance(d, dict):
            for k, v in d.items():
                if isinstance(v, dict):
                    print(f"{prefix}{k}: (dict)")
                    show_keys(v, prefix + "  ")
                elif isinstance(v, list):
                    print(f"{prefix}{k}: (list, {len(v)} items)")
                else:
                    val_str = str(v)[:60] if v else 'None'
                    print(f"{prefix}{k}: {val_str}")
    show_keys(sample)

# Check how many AYUSH standards we have fetched vs total
print(f"\n{'='*80}")
print(f"COVERAGE: {len(items)} / {total} AYUSH standards fetched ({100*len(items)/total:.1f}%)")
print(f"Detail files stored: {len(detail_files)}")
print(f"{'='*80}")
