
# **Backtrack Backup App**

**Backtrack** is a robust Python script that automatically monitors a directory for changes and creates regular backups, ensuring your data is always safe. It performs virus scanning using **ClamAV** and **Maldet** before making backups. It checks for file changes every 5 minutes and triggers a backup if there are any new changes, removing the old backup to save space.

### Features

- **Automatic Backup**: Watches a specified directory for file changes and backs up automatically.
- **Virus Scanning**: Integrates with **ClamAV** and **Maldet** to scan for malware before backing up.
- **Efficient**: Only creates a backup when changes are detected in the source directory.
- **Log System**: Tracks all backup actions and scans, including any errors, in a detailed log.
- **Directory Monitoring**: Continuously monitors the directory for new files or modifications.

### Prerequisites

Before running **Backtrack**, ensure you have the following installed on your system:

1. **Python 3**: Ensure Python 3 is installed.
2. **ClamAV**: ClamAV must be installed for virus scanning.
3. **Maldet**: Maldet (Linux Malware Detect) must be installed.
4. **inotify**: Used for monitoring file system changes.
5. **colorama**: A library for colored output in the terminal.

To install the required dependencies, you can use the following command:

```bash
pip install colorama inotify
```

To install **ClamAV** and **Maldet**, use:

```bash
sudo apt-get install clamav maldet
```

### Usage

1. **Run the script** with the following command:

```bash
python3 backtrack.py <source_directory> <backup_directory>
```

   - `<source_directory>`: The directory you want to monitor and back up.
   - `<backup_directory>`: The location where the backup will be stored.

   **Example**:

   ```bash
   python3 backtrack.py /home/user/documents /tmp/backups
   ```

2. **What happens next**:
   - The script will first perform a virus scan (with ClamAV and Maldet) on the `source_directory`.
   - After the scan, it will create a backup of the directory.
   - The script will monitor the directory for new files or changes. If a change is detected, it will perform a scan and backup again, removing any old backups if necessary.

3. **Logs**:
   - All backup and scan actions are logged in `/tmp/backtrack_log.txt`.

### Sample Output

When running the script, you'll see output like this:

```bash
Starting virus scan of /home/user/documents with ClamAV and Maldet...
ClamAV scan result: /home/user/documents/index.html: OK
ClamAV scan result: /home/user/documents/style.css: OK
Maldet scan result: Scanned 5 files.
Backup created: /tmp/backups/backup_20250124_1240.tar.gz
sha256sum calculated and saved.
Removed old backup: backup_20250124_1234.tar.gz
```


### Troubleshooting

- **ClamAV not installed**: If the script can't find ClamAV, you may need to install it using `sudo apt-get install clamav` or a similar command depending on your OS.
- **Maldet not installed**: Similarly, install Maldet using `sudo apt-get install maldet`.

