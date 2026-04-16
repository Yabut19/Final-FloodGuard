import sys

filepath = r"c:\xampp\htdocs\FloodGuard\FloodGuard\frontend\mobile\App.js"
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
skip = False
for i, line in enumerate(lines):
    if "styles.bottomNav" in line:
        skip = True
        # backtrack to remove the opening <View
        while out:
            last = out.pop()
            if "<View" in last:
                break
        continue
    
    if skip:
        if "</SafeAreaView>" in line:
            skip = False
            out.append(line)
        continue
    
    out.append(line)

with open(filepath, "w", encoding="utf-8") as f:
    f.writelines(out)

print("Bottom navigation stripped successfully.")
