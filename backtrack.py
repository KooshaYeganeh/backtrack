import os
import time
import subprocess
import hashlib
import inotify.adapters
import sys
from datetime import datetime
from colorama import init, Fore

# Initialize colorama
init(autoreset=True)

# Log file
log_file = '/tmp/backtrack_log.txt'

# Function to write logs with colored output
def log(message, color=Fore.WHITE):
    with open(log_file, 'a') as logf:
        logf.write(f"{datetime.now()} - {message}\n")
    print(f"{color}{datetime.now()} - {message}")

# Function to scan the directory with ClamAV, Maldet
def scan_directory(source_dir):
    log(f"Scanning directory: {source_dir}", Fore.CYAN)
    
    # Inform the user that the scan is starting
    print(Fore.YELLOW + f"Starting virus scan of {source_dir} with ClamAV and Maldet...")

    # ClamAV scan with verbose flag to show files being scanned
    clamav_scan = subprocess.run(["clamscan", "--remove", "--infected", "--recursive", "--verbose", source_dir], capture_output=True, text=True)
    if clamav_scan.stdout:
        log(f"ClamAV scan result: {clamav_scan.stdout}", Fore.YELLOW)

# Function to calculate sha256sum
def calculate_sha256sum(directory):
    sha256sum = ""
    for root, dirs, files in os.walk(directory):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, "rb") as f:
                sha256sum += hashlib.sha256(f.read()).hexdigest()
    return sha256sum

# Function to perform the backup
def perform_backup(source_dir, backup_dir):
    timestamp = datetime.now().strftime('%Y%m%d_%H%M')
    backup_name = f"backup_{timestamp}.tar.gz"
    
    log(f"Starting backup...", Fore.GREEN)
    
    # Create a compressed backup of the source directory
    subprocess.run(['tar', '-czf', os.path.join(backup_dir, backup_name), source_dir])
    log(f"Backup created: {os.path.join(backup_dir, backup_name)}", Fore.GREEN)
    
    # Calculate sha256sum and save it to file
    sha256sum = calculate_sha256sum(source_dir)
    with open(os.path.join(backup_dir, f"sha256sum_{timestamp}.txt"), 'w') as f:
        f.write(sha256sum)
    log(f"sha256sum calculated and saved.", Fore.GREEN)

    # Remove old backup if it exists
    old_backups = sorted([f for f in os.listdir(backup_dir) if f.startswith('backup_')], reverse=True)
    if len(old_backups) > 1:  # Keep only the latest one
        old_backup = old_backups[1]
        os.remove(os.path.join(backup_dir, old_backup))
        log(f"Removed old backup: {old_backup}", Fore.RED)

# Function to check if a backup is needed
def check_and_backup(source_dir, backup_dir):
    # Get the current sha256sum of the directory
    current_sha256 = calculate_sha256sum(source_dir)
    
    # Try to read the previous sha256sum (if exists)
    last_sha256 = None
    try:
        with open(os.path.join(backup_dir, 'sha256sum_latest.txt'), 'r') as f:
            last_sha256 = f.read()
    except FileNotFoundError:
        last_sha256 = None
    
    # If there's no previous sha256sum or they differ, perform a backup
    if last_sha256 != current_sha256:
        perform_backup(source_dir, backup_dir)
        # Update the latest sha256sum
        with open(os.path.join(backup_dir, 'sha256sum_latest.txt'), 'w') as f:
            f.write(current_sha256)
    else:
        log(f"No changes detected, skipping backup.", Fore.RED)

# Function to handle directory events and trigger backup
def handle_directory_changes(source_dir, backup_dir):
    i = inotify.adapters.Inotify()
    i.add_watch(source_dir)
    
    try:
        log("Script execution started. Watching for changes...", Fore.GREEN)
        for event in i.event_gen(yield_nones=False):
            _, type_names, path, _ = event
            if 'IN_MODIFY' in type_names or 'IN_CREATE' in type_names or 'IN_DELETE' in type_names:
                log(f"Change detected: {type_names} on {path}", Fore.YELLOW)
                check_and_backup(source_dir, backup_dir)
    finally:
        i.remove_watch(source_dir)
        i.close()

# Main execution
if __name__ == '__main__':
    # Check for command-line arguments
    if len(sys.argv) != 3:
        log("Usage: python3 backtrack.py <source_directory> <backup_directory>", Fore.RED)
        sys.exit(1)

    # Get source and backup directories from command-line arguments
    source_dir = sys.argv[1]
    backup_dir = sys.argv[2]
    
    # Ensure the backup directory exists
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)
        log(f"Created backup directory: {backup_dir}", Fore.GREEN)
    
    # Initial scan and backup
    scan_directory(source_dir)
    perform_backup(source_dir, backup_dir)
    
    # Start the monitoring and backup process
    handle_directory_changes(source_dir, backup_dir)

