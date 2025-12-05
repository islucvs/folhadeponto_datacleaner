with open("not_treated.txt", "r", encoding="utf-8") as infile:
    lines = infile.readlines()

filtered_lines = [line for line in lines if len(line.rstrip('\n')) >= 38]

with open("treated.txt", "w", encoding="utf-8") as outfile:
    outfile.writelines(filtered_lines)

print(f"Kept {len(filtered_lines)} lines with 38+ characters")