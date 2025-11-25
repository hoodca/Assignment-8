def _parse_date_to_month(date_str):
    """Return 'YYYY-MM' from a date-like string using only builtins.

    Strategy: extract leading digits and interpret YYYYMMDD (or at least
    YYYYMM). If less information is available, return None.
    """
    if not date_str:
        return None
    digits = ''.join(ch for ch in date_str if ch.isdigit())
    if len(digits) >= 6:
        # prefer YYYYMMDD if available
        y = digits[0:4]
        m = digits[4:6]
        try:
            yi = int(y)
            mi = int(m)
            if 1 <= mi <= 12:
                return '%04d-%02d' % (yi, mi)
        except Exception:
            return None
    return None


def _parse_csv_row(line):
    fields = []
    cur = []
    in_quote = False
    i = 0
    L = len(line)
    while i < L:
        ch = line[i]
        if in_quote:
            if ch == '"':
                # lookahead for escaped quote
                if i + 1 < L and line[i + 1] == '"':
                    cur.append('"')
                    i += 1
                else:
                    in_quote = False
            else:
                cur.append(ch)
        else:
            if ch == '"':
                in_quote = True
            elif ch == ',':
                fields.append(''.join(cur))
                cur = []
            else:
                cur.append(ch)
        i += 1
    fields.append(''.join(cur))
    # strip possible trailing CR/LF from last field
    if fields and fields[-1].endswith('\n'):
        fields[-1] = fields[-1].rstrip('\r\n')
    return fields


def states_above_threshold_by_month(input_csv, output_csv, threshold,
                                    date_col='date', state_col='state', value_col='totalTestResults'):
    monthly_max = {}  # key=(month, state) -> int value
    months_set = {}  # map month -> True for ordering later

    with open(input_csv, 'r', encoding='utf-8') as fh:
        # read header
        header_line = fh.readline()
        if not header_line:
            raise ValueError('input CSV is empty')
        header = _parse_csv_row(header_line)
        # map column names to indices
        col_index = {}
        for idx, name in enumerate(header):
            col_index[name] = idx

        # required columns must exist
        if date_col not in col_index or state_col not in col_index or value_col not in col_index:
            raise ValueError('missing required columns in CSV header')

        date_idx = col_index[date_col]
        state_idx = col_index[state_col]
        value_idx = col_index[value_col]

        for raw in fh:
            if not raw.strip():
                continue
            fields = _parse_csv_row(raw)
            # guard: skip lines with too few fields
            if len(fields) <= max(date_idx, state_idx, value_idx):
                continue
            date_raw = fields[date_idx]
            month = _parse_date_to_month(date_raw)
            if not month:
                continue
            state = fields[state_idx].strip()
            if not state:
                continue
            val_raw = fields[value_idx].strip()
            if val_raw == '':
                continue
            # parse numeric value conservatively
            try:
                # some values may be floats; int(float(...)) works for both
                v = int(float(val_raw))
            except Exception:
                continue

            months_set[month] = True
            key = (month, state)
            if key in monthly_max:
                if v > monthly_max[key]:
                    monthly_max[key] = v
            else:
                monthly_max[key] = v

    months = list(months_set.keys())
    months.sort()

    out_lines = []
    out_lines.append('month,states,count')
    for month in months:
        states = []
        for (m, s), val in monthly_max.items():
            if m == month and val > threshold:
                states.append(s)
        states.sort()
        out_lines.append('%s,%s,%d' % (month, ';'.join(states), len(states)))

    with open(output_csv, 'w', encoding='utf-8') as outfh:
        outfh.write('\n'.join(out_lines))

    return output_csv


if __name__ == '__main__':
    # Default run (no imports/argparse): process the dataset with a 1,000,000 threshold
    # Update these paths if you want to run on a different file.
    input_path = 'c:\\Users\\camjh\\Downloads\\extracted_files\\usscv19d.csv'
    output_path = 'c:\\Users\\camjh\\Downloads\\extracted_files\\states_above_1M_by_month_noimports.csv'
    threshold = 1000000
    try:
        out = states_above_threshold_by_month(input_path, output_path, threshold)
        print('Wrote:', out)
    except Exception as exc:
        print('Error:', exc)
