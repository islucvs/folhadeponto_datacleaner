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
    # Read PIS data with flexible column handling
    pis_data = defaultdict(list)
    try:
        with open('pis_data.csv', 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            header = next(reader)  # Read header
            
            # Determine column indices
            try:
                dia_index = header.index("Dia")
                hora_index = header.index("Hora")
                pis_index = header.index("PIS")
            except ValueError:
                dia_index = 1
                hora_index = 2
                pis_index = 3
            
            for row_num, row in enumerate(reader, 2):
                if len(row) < max(dia_index, hora_index, pis_index) + 1:
                    continue
                
                try:
                    date_str = row[dia_index]
                    time = row[hora_index]
                    pis = row[pis_index]
                    day, month, year = parse_date(date_str)
                    pis_data[pis].append((day, time))
                except (ValueError, IndexError) as e:
                    print(f"PIS data row {row_num} error: {e}")
                    continue

    except FileNotFoundError:
        print("pis_data.csv not found")
        return
    except Exception as e:
        print(f"Error reading pis_data.csv: {e}")
        return

    # Process and pair PIS times
    for pis in pis_data:
        pis_data[pis].sort(key=lambda x: (x[0], x[1]))
    
    def pair_times(entries):
        paired = {}
        days = set(day for day, _ in entries)
        for day in days:
            times = [time for d, time in entries if d == day]
            morning_times = [t for t in times if is_morning(t)]
            afternoon_times = [t for t in times if not is_morning(t)]
            
            entrada = min(morning_times) if morning_times else ''
            saida = max(afternoon_times) if afternoon_times else ''
            
            paired[day] = (entrada, saida)
        return paired
    
    paired_pis_data = {}
    for pis, entries in pis_data.items():
        paired_pis_data[pis] = pair_times(entries)

    # Generate output header
    output_header = ["ID", "CPF", "PIS", "Nome", "Cargo", "Lotação"]
    for day in range(1, 32):
        output_header.extend([f"Dia{day}_Entrada", f"Dia{day}_Saida"])

    # Process employee data - preserve existing entries
    try:
        with open('employee_data.csv', 'r', encoding='utf-8') as csv_in, \
             open('employee_data_processed.csv', 'w', newline='', encoding='utf-8') as csv_out:
            
            reader = csv.reader(csv_in)
            writer = csv.writer(csv_out)
            writer.writerow(output_header)
            
            # Read employee header to find column positions
            emp_header = next(reader)
            try:
                pis_col = emp_header.index("PIS")
            except ValueError:
                pis_col = 2  # Fallback to column 2
            
            # Create column map for days
            day_columns = {}
            for day in range(1, 32):
                try:
                    entrada_col = emp_header.index(f"Dia{day}_Entrada")
                    saida_col = emp_header.index(f"Dia{day}_Saida")
                    day_columns[day] = (entrada_col, saida_col)
                except ValueError:
                    # If day columns don't exist, calculate positions
                    entrada_col = 6 + (day - 1) * 2
                    saida_col = entrada_col + 1
                    day_columns[day] = (entrada_col, saida_col)
            
            for row_num, row in enumerate(reader, 2):
                if len(row) < 6:
                    print(f"Warning: Employee row {row_num} has insufficient columns - skipping")
                    writer.writerow(row)
                    continue
                
                # Create a new row with existing data
                new_row = row
                
                # Extend row if needed for day columns
                max_col = max(max(entrada, saida) for entrada, saida in day_columns.values())
                while len(new_row) <= max_col:
                    new_row.append('')
                
                if pis_col < len(row):
                    pis = row[pis_col]
                else:
                    pis = ""
                
                if pis in paired_pis_data:
                    for day, (entrada_col, saida_col) in day_columns.items():
                        # Ensure columns exist in row
                        while len(new_row) <= max(entrada_col, saida_col):
                            new_row.append('')
                        
                        current_entrada = new_row[entrada_col].strip()
                        current_saida = new_row[saida_col].strip()
                        
                        # Only update if both columns are empty
                        if not current_entrada and not current_saida:
                            entrada, saida = paired_pis_data[pis].get(day, ('', ''))
                            if entrada:
                                new_row[entrada_col] = entrada
                            if saida:
                                new_row[saida_col] = saida
                
                writer.writerow(new_row)

        print("Processing complete. Output saved to employee_data_processed.csv")
        print("Existing data was preserved, only empty day slots were updated")

    except FileNotFoundError:
        print("employee_data.csv not found")
    except Exception as e:
        print(f"Error processing employee data: {e}")

if __name__ == "__main__":
    main()
