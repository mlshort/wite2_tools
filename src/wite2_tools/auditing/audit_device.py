import csv
import math
from typing import Set

from wite2_tools import get_csv_dict_stream
from wite2_tools import ENCODING_TYPE
from wite2_tools.utils import parse_int



def apply_anti_armor_fix_with_validation(device_input_path: str,
                                         output_path: str,
                                         target_types: Set | None,
                                         apply_fix: bool = False):
    """
    Applies the antiArmor = pen * 0.8 fix and validates the results.
    """
    # Track statistics for validation
    stats = {} # {type_id: {'min': val, 'max': val, 'count': 0}}

    # Initialize the generator
    dev_stream = get_csv_dict_stream(device_input_path)

    # 1. Grab the reader object first (the first yield in your generator)
    # reader_obj = next(device_gen)
    # reader = cast(csv.DictReader, reader_obj)
    fieldnames = dev_stream.fieldnames

    # 2. Open output file for writing
    with open(output_path, mode='w', encoding=ENCODING_TYPE, newline='') as f_out:
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        # 3. Process rows from the generator
        for _, row in dev_stream.rows:
            try:
                dev_type = parse_int(row.get('type'), -1)
                dev_pen = parse_int(row.get('pen'), 0)

                # Apply fix for specified types
                if target_types and dev_type in target_types and dev_pen > 0:
                    new_aa = math.floor((dev_pen * 0.8) + 0.5)
                    if apply_fix:
                        row['antiArmor'] = str(new_aa)

                    # Update validation stats
                    if dev_type not in stats:
                        stats[dev_type] = {'min': new_aa, 'max': new_aa, 'count': 0}

                    stats[dev_type]['min'] = min(stats[dev_type]['min'], new_aa)
                    stats[dev_type]['max'] = max(stats[dev_type]['max'], new_aa)
                    stats[dev_type]['count'] += 1

                writer.writerow(row)
            except (ValueError, TypeError):
                writer.writerow(row)

    # 4. Display Validation Summary
    print("\n" + "="*50)
    print(f"{'TYPE':<10} {'COUNT':<10} {'MIN AA':<10} {'MAX AA':<10}")
    print("-"*50)

    if not stats:
        print("No devices were updated.")
    else:
        for t_id in sorted(stats.keys()):
            s = stats[t_id]
            print(f"{t_id:<10} {s['count']:<10} {s['min']:<10} {s['max']:<10}")

    print("="*50)
    print(f"Fixed file generated: {output_path}")

if __name__ == "__main__":
    INPUT_FILE = '1941 Campaign_device.csv'
    OUTPUT_FILE = '1941 Campaign_device_FIXED.csv'
    # Target Ground Elements, squads, and light guns
    TARGET_TYPES = {1, 2, 3, 5, 6}

    apply_anti_armor_fix_with_validation(INPUT_FILE,
                                         OUTPUT_FILE,
                                         TARGET_TYPES)
