#!/usr/bin/env python3
"""
A2L to PID List Converter using pya2l
Refactored to use pya2l library for robust A2L file parsing instead of manual parsing.
"""

import sys
import csv
from pathlib import Path

try:
    from pya2l.parser import A2lParser as Parser
    PYA2L_AVAILABLE = True
except ImportError:
    PYA2L_AVAILABLE = False
    Parser = None


def extract_measurements_and_characteristics(a2l_file_path):
    """
    Extract measurements and characteristics from A2L file using pya2l.
    
    Args:
        a2l_file_path (str): Path to the A2L file
        
    Returns:
        tuple: (measurements_dict, characteristics_dict)
    """
    # If pya2l is not available, fall back to manual parsing immediately
    if not PYA2L_AVAILABLE:
        print("pya2l library not available. Using fallback parsing method...")
        return fallback_parse_a2l(a2l_file_path)
    
    measurements = {}
    characteristics = {}
    
    try:
        # Read A2L file as binary (required by pya2l)
        with open(a2l_file_path, 'rb') as f:
            a2l_content = f.read()
        
        # Parse A2L file using pya2l
        with Parser() as parser:
            ast = parser.tree_from_a2l(a2l_content)
            
            # Navigate through PROJECT -> MODULE structure
            if hasattr(ast, 'PROJECT') and hasattr(ast.PROJECT, 'MODULE'):
                modules = ast.PROJECT.MODULE if isinstance(ast.PROJECT.MODULE, list) else [ast.PROJECT.MODULE]
                
                for module in modules:
                    # Extract MEASUREMENT objects
                    if hasattr(module, 'MEASUREMENT'):
                        measurement_list = module.MEASUREMENT if isinstance(module.MEASUREMENT, list) else [module.MEASUREMENT]
                        
                        for measurement in measurement_list:
                            name = getattr(measurement.Name, 'Value', str(measurement.Name))
                            address = None
                            
                            # Try to get address from various possible locations
                            if hasattr(measurement, 'ECU_ADDRESS'):
                                if hasattr(measurement.ECU_ADDRESS, 'Value'):
                                    address = hex(measurement.ECU_ADDRESS.Value)
                                else:
                                    address = hex(measurement.ECU_ADDRESS)
                            
                            measurements[name] = {
                                'name': name,
                                'address': address,
                                'long_identifier': getattr(getattr(measurement, 'LongIdentifier', None), 'Value', ''),
                                'unit': getattr(getattr(measurement, 'Unit', None), 'Value', ''),
                                'data_type': getattr(getattr(measurement, 'Datatype', None), 'Value', ''),
                                'lower_limit': getattr(getattr(measurement, 'LowerLimit', None), 'Value', ''),
                                'upper_limit': getattr(getattr(measurement, 'UpperLimit', None), 'Value', ''),
                            }
                    
                    # Extract CHARACTERISTIC objects
                    if hasattr(module, 'CHARACTERISTIC'):
                        characteristic_list = module.CHARACTERISTIC if isinstance(module.CHARACTERISTIC, list) else [module.CHARACTERISTIC]
                        
                        for characteristic in characteristic_list:
                            name = getattr(characteristic.Name, 'Value', str(characteristic.Name))
                            address = None
                            
                            # Try to get address from various possible locations
                            if hasattr(characteristic, 'ECU_ADDRESS'):
                                if hasattr(characteristic.ECU_ADDRESS, 'Value'):
                                    address = hex(characteristic.ECU_ADDRESS.Value)
                                else:
                                    address = hex(characteristic.ECU_ADDRESS)
                            
                            characteristics[name] = {
                                'name': name,
                                'address': address,
                                'long_identifier': getattr(getattr(characteristic, 'LongIdentifier', None), 'Value', ''),
                                'unit': getattr(getattr(characteristic, 'Unit', None), 'Value', ''),
                                'lower_limit': getattr(getattr(characteristic, 'LowerLimit', None), 'Value', ''),
                                'upper_limit': getattr(getattr(characteristic, 'UpperLimit', None), 'Value', ''),
                            }
                            
    except FileNotFoundError:
        print(f"Error: A2L file not found: {a2l_file_path}")
        return {}, {}
    except Exception as e:
        print(f"Error parsing A2L file '{a2l_file_path}': {e}")
        print("Falling back to original parsing method...")
        return fallback_parse_a2l(a2l_file_path)
    
    return measurements, characteristics


def fallback_parse_a2l(a2l_file_path):
    """
    Fallback to original manual parsing method if pya2l fails.
    
    Args:
        a2l_file_path (str): Path to the A2L file
        
    Returns:
        tuple: (measurements_dict, characteristics_dict) - simplified format
    """
    items = {}
    
    try:
        with open(a2l_file_path, "r", encoding="utf-8-sig", errors="surrogateescape") as a2l_file:
            current_state = 0
            variable_name = ""
            a2l_lines = a2l_file.readlines()
            
            for current_line in a2l_lines:
                if current_state == 0:
                    current_line = current_line.strip()
                    begin_pos = current_line.find("/begin")
                    measure_pos = current_line.find("MEASUREMENT")
                    char_pos = current_line.find("CHARACTERISTIC")
                    
                    if begin_pos == 0:
                        if measure_pos >= 0:
                            variable_name = current_line[measure_pos + 12:].strip()
                            current_state = 1
                        elif char_pos >= 0:
                            variable_name = current_line[char_pos + 15:].strip()
                            current_state = 1

                elif current_state == 1:
                    current_line = current_line.strip()
                    begin_pos = current_line.find("/begin")
                    if begin_pos == 0:
                        current_state = 2

                elif current_state == 2:
                    current_line = current_line.strip()
                    add_pos = current_line.find("0x")
                    if add_pos == 0:
                        items[variable_name] = {
                            'name': variable_name,
                            'address': current_line,
                            'long_identifier': '',
                            'unit': '',
                            'lower_limit': '',
                            'upper_limit': '',
                        }
                        current_state = 0
                        
    except Exception as e:
        print(f"Error in fallback parsing: {e}")
        return {}, {}
    
    # Return as measurements for compatibility
    return items, {}


def load_template_csv(template_file_path):
    """
    Load the template CSV file containing PID definitions.
    
    Args:
        template_file_path (str): Path to the template CSV file
        
    Returns:
        list: List of dictionaries containing PID data
    """
    pid_list = []
    
    try:
        with open(template_file_path, "r", encoding="utf-8-sig", errors="surrogateescape") as f:
            reader = csv.DictReader(f)
            for row in reader:
                pid_list.append(row)
    except FileNotFoundError:
        print(f"Error: Template file not found: {template_file_path}")
        sys.exit(1)
    except Exception as e:
        print(f"Error reading template file: {e}")
        sys.exit(1)
    
    return pid_list


def update_pid_list_with_a2l_data(pid_list, measurements, characteristics):
    """
    Update PID list with data extracted from A2L file.
    
    Args:
        pid_list (list): List of PID dictionaries from template
        measurements (dict): Measurements extracted from A2L
        characteristics (dict): Characteristics extracted from A2L
        
    Returns:
        int: Number of PIDs updated with A2L data
    """
    # Combine measurements and characteristics
    all_items = {**measurements, **characteristics}
    updated_count = 0
    
    # Update PID list with found addresses and data
    for pid in pid_list:
        pid_name = pid.get('Name', '').strip()
        if pid_name in all_items:
            item = all_items[pid_name]
            
            # Update address if found
            if item.get('address'):
                pid['Address'] = item['address']
                updated_count += 1
            
            # Update other fields if they're empty in the template
            if item.get('unit') and not pid.get('Unit', '').strip():
                pid['Unit'] = item['unit']
            
            # Could add more field mappings here in the future
            # if item.get('lower_limit') and not pid.get('ProgMin', '').strip():
            #     pid['ProgMin'] = str(item['lower_limit'])
            # if item.get('upper_limit') and not pid.get('ProgMax', '').strip():
            #     pid['ProgMax'] = str(item['upper_limit'])
    
    return updated_count


def write_output_csv(pid_list, output_file_path):
    """
    Write the updated PID list to output CSV file.
    
    Args:
        pid_list (list): List of PID dictionaries
        output_file_path (str): Path to output CSV file
    """
    try:
        with open(output_file_path, 'w', newline='', encoding='utf-8') as f:
            fieldnames = ["Name", "Unit", "Equation", "Format", "Address", "Length", 
                         "Signed", "ProgMin", "ProgMax", "WarnMin", "WarnMax", 
                         "Smoothing", "Enabled", "Tabs", "Assign To"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for pid in pid_list:
                writer.writerow(pid)
    except Exception as e:
        print(f"Error writing output file: {e}")
        sys.exit(1)


def main():
    """Main function."""
    if len(sys.argv) != 4:
        print("Usage: python a2l2pid.py <a2l_file> <template_csv> <output_csv>")
        print("\nThis script converts A2L files to PID lists using a template CSV.")
        print("It uses the pya2l library for robust A2L parsing with fallback to manual parsing.")
        sys.exit(1)
    
    a2l_file = sys.argv[1]
    template_file = sys.argv[2]
    output_file = sys.argv[3]
    
    # Validate input files exist
    if not Path(a2l_file).exists():
        print(f"Error: A2L file does not exist: {a2l_file}")
        sys.exit(1)
    
    if not Path(template_file).exists():
        print(f"Error: Template file does not exist: {template_file}")
        sys.exit(1)
    
    print(f"Processing A2L file: {a2l_file}")
    print(f"Using template: {template_file}")
    print(f"Output file: {output_file}")
    
    # Load template PID list
    print("Loading template CSV...")
    pid_list = load_template_csv(template_file)
    print(f"Loaded {len(pid_list)} PIDs from template")
    
    # Extract data from A2L file
    print("Parsing A2L file...")
    measurements, characteristics = extract_measurements_and_characteristics(a2l_file)
    
    total_items = len(measurements) + len(characteristics)
    print(f"Extracted {len(measurements)} measurements and {len(characteristics)} characteristics ({total_items} total)")
    
    # Update PID list with A2L data
    print("Updating PID list with A2L data...")
    updated_count = update_pid_list_with_a2l_data(pid_list, measurements, characteristics)
    print(f"Updated {updated_count} PIDs with A2L data")
    
    # Write output CSV
    print("Writing output CSV...")
    write_output_csv(pid_list, output_file)
    print(f"Successfully created: {output_file}")


if __name__ == "__main__":
    main()
