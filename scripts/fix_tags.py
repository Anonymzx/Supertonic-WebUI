import os

# Find and remove artifact XML tags from all Python files
markers = [b'</write_to_file', b'<write_to_file', b'</final_file_content', b'<final_file_content', b'<artifact', b'</artifact', b'<replace_in_file', b'</replace_in_file']

for root, dirs, files in os.walk('backend'):
    for f in files:
        if not f.endswith('.py'):
            continue
        fp = os.path.join(root, f)
        with open(fp, 'rb') as fh:
            data = fh.read()
        
        changed = False
        for m in markers:
            while m in data:
                idx = data.find(m)
                # Find end of tag (either > or next line)
                end = data.find(b'>', idx)
                if end >= 0:
                    data = data[:idx] + data[end+1:]
                else:
                    data = data[:idx]
                changed = True
        
        if changed:
            with open(fp, 'wb') as fh:
                fh.write(data.strip() + b'\n')
            print(f'FIXED: {f}')

print('Done fixing tags')