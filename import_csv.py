import csv
from collections import defaultdict
from datetime import datetime

def parse_date(date_str):
    """Parse date from DDMMYYYY format (7 or 8 digits)"""
    try:
        clean_date = ''.join(c for c in date_str if c.isdigit())
        
        if len(clean_date) == 7:  # DMMYYYY format
            day = int(clean_date[0])
            month = int(clean_date[1:3])
            year = int(clean_date[3:])
        elif len(clean_date) == 8:  # DDMMYYYY format
            day = int(clean_date[:2])
            month = int(clean_date[2:4])
            year = int(clean_date[4:])
        else:
            raise ValueError(f"Date must be 7 or 8 digits (got {len(clean_date)}): {date_str}")
        
        return day, month, year
    except ValueError as e:
        raise ValueError(f"Invalid date format (expected DMMYYYY or DDMMYYYY): {date_str}") from e

def is_morning(time_str):
    """Check if time is before 10:00 AM"""
    try:
        time_obj = datetime.strptime(time_str, '%H:%M').time()
        return time_obj < datetime.strptime('10:00', '%H:%M').time()
    except ValueError:
        return False

def main():
    # Read PIS data
    pis_data = defaultdict(list)
    try:
        with open('pis_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            for row_num, row in enumerate(reader, 2):
                if len(row) < 5:
                    continue
                
                try:
                    date_str, time, pis = row[1], row[2], row[3]
                    day, month, year = parse_date(date_str)
                    pis_data[pis].append((day, time))
                except ValueError as e:
                    print(f"Row {row_num} error: {e}")
                    continue

    except FileNotFoundError:
        print("pis_data.csv not found")
        return

    # Sort and pair times
    for pis in pis_data:
        pis_data[pis].sort(key=lambda x: (x[0], x[1]))

    def pair_times(entries):
        paired = {}
        i = 0
        while i < len(entries):
            day, time = entries[i]
            
            # Find all entries for this day
            day_entries = [t for d, t in entries if d == day]
            morning_entries = [t for t in day_entries if is_morning(t)]
            afternoon_entries = [t for t in day_entries if not is_morning(t)]
            
            # Take earliest morning as entrada, latest afternoon as saida
            entrada = min(morning_entries) if morning_entries else ''
            saida = max(afternoon_entries) if afternoon_entries else ''
            
            paired[day] = (entrada, saida)
            i += len(day_entries)  # Skip all entries for this day
        
        return paired

    # Generate output header
    output_header = ["ID", "CPF", "PIS", "Nome", "Cargo", "Lotação"]
    for day in range(1, 32):
        output_header.extend([f"Dia{day}_Entrada", f"Dia{day}_Saida"])

    # Process employee data
    try:
        with open('employee_data.csv', 'r', encoding='utf-8') as csv_in, \
             open('employee_data_processed.csv', 'w', newline='', encoding='utf-8') as csv_out:
            
            reader = csv.reader(csv_in)
            writer = csv.writer(csv_out)
            writer.writerow(output_header)
            
            for row_num, row in enumerate(reader, 1):
                if row_num == 1:  # Skip header
                    continue
                
                if len(row) < 6:
                    continue
                
                new_row = row[:6] + [''] * 62
                pis = row[2]
                
                if pis in pis_data:
                    paired_times = pair_times(pis_data[pis])
                    
                    for day, (entrada, saida) in paired_times.items():
                        if 1 <= day <= 31:
                            entrada_col = 6 + (day - 1) * 2
                            saida_col = entrada_col + 1
                            
                            if entrada_col < len(new_row):
                                new_row[entrada_col] = entrada
                            if saida_col < len(new_row):
                                new_row[saida_col] = saida
                
                writer.writerow(new_row)

        print("Processing complete. Output saved to employee_data_processed.csv")

    except FileNotFoundError:
        print("employee_data.csv not found")

if __name__ == "__main__":
    main()
