import os
import subprocess
import re

tag_start_markers = [
    b'</write_to_file>',
    b'<write_to_file>',
    b'</final_file_content>',
    b'<final_file_content>',
    b'<final_file_content',
    b'<artifact>',
    b'</artifact>',
    b'<replace_in_file>',
    b'</replace_in_file>',
]

for root, dirs, files in os.walk('backend'):
    for f in sorted(files):
        if not f.endswith('.py'):
            continue
        fp = os.path.join(root, f)

        with open(fp, 'rb') as fh:
            raw = fh.read()

        fixed = False
        for marker in tag_start_markers:
            while True:
                idx = raw.find(marker)
                if idx < 0:
                    break
                print(f'FOUND marker in {f} at byte {idx}: {marker}')
                marker_end = idx + len(marker)
                raw = raw[:idx] + raw[marker_end:]
                fixed = True

        # Also remove any remaining </write_to_file lines
        lines = raw.split(b'\n')
        clean_lines = [l for l in lines if b'</write_to_file>' not in l and b'<write_to_file>' not in l]
        if len(clean_lines) != len(lines):
            fixed = True
            raw = b'\n'.join(clean_lines)

        if fixed:
            raw = raw.strip() + b'\n'
            with open(fp, 'wb') as fh:
                fh.write(raw)
            print(f'  -> FIXED {f}')
        else:
            print(f'  CLEAN {f}')

print()
print('Syntax validation...')
all_ok = True
for root, dirs, files in os.walk('backend'):
    for f in sorted(files):
        if not f.endswith('.py'):
            continue
        fp = os.path.join(root, f)
        r = subprocess.run(['python', '-m', 'py_compile', fp], capture_output=True, text=True)
        if r.returncode == 0:
            print(f'  OK: {f}')
        else:
            print(f'  FAIL: {f}')
            print(f'    {r.stderr.strip()[:200]}')
            all_ok = False

if all_ok:
    print()
    print('All files pass!')
else:
    print()
    print('Some files still have issues!')
    exit(1)
</write_to_file>