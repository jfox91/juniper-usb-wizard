#!/usr/bin/env python3
"""
Juniper USB Wizard - A tool to properly format USB drives and copy Juniper files
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path
from typing import List, Optional, Tuple

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, Horizontal
from textual.widgets import Header, Footer, Button, Static, Label, ListItem, ListView
from textual.screen import Screen
from textual import on
from textual.binding import Binding


class DriveInfo:
    """Information about a storage device"""
    def __init__(self, device: str, size: str, mountpoint: str, fstype: str):
        self.device = device
        self.size = size
        self.mountpoint = mountpoint
        self.fstype = fstype

    def __str__(self):
        return f"{self.device} - {self.size} ({self.fstype or 'unformatted'})"

    @property
    def size_gb(self) -> float:
        """Convert size to GB for comparison"""
        size_str = self.size.upper()
        if 'T' in size_str:
            return float(size_str.replace('T', '')) * 1024
        elif 'G' in size_str:
            return float(size_str.replace('G', ''))
        elif 'M' in size_str:
            return float(size_str.replace('M', '')) / 1024
        return 0


class FileSelectionScreen(Screen):
    """Screen for selecting a Juniper file"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    def __init__(self, files: List[Path]):
        super().__init__()
        self.files = files

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select Juniper File", classes="title"),
            ListView(
                *[ListItem(Label(f.name)) for f in self.files],
                id="file_list"
            ),
            Static("\n[dim]Press ESC to quit[/dim]", classes="help-text"),
            id="file_container"
        )
        yield Footer()

    @on(ListView.Selected, "#file_list")
    def on_file_selected(self, event: ListView.Selected) -> None:
        """Handle file selection"""
        selected_file = self.files[event.list_view.index]
        self.app.selected_file = selected_file
        self.app.push_screen(DriveSelectionScreen())


class DriveSelectionScreen(Screen):
    """Screen for selecting a USB drive"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Select USB Drive", classes="title"),
            Static(f"File: {self.app.selected_file.name}", classes="info"),
            Static("", id="loading", classes="info"),
            ListView(id="drive_list"),
            Static("\n[dim]Press ESC to go back[/dim]", classes="help-text"),
            id="drive_container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Load drives when screen is mounted"""
        loading = self.query_one("#loading", Static)
        loading.update("Loading drives...")
        self.scan_drives()

    def scan_drives(self) -> None:
        """Scan for available USB drives"""
        drives = self.get_usb_drives()

        loading = self.query_one("#loading", Static)
        drive_list = self.query_one("#drive_list", ListView)

        if not drives:
            loading.update("[red]No USB drives found![/red]")
            return

        loading.update(f"Found {len(drives)} drive(s)")

        for drive in drives:
            mount_info = f" (mounted at {drive.mountpoint})" if drive.mountpoint else ""
            label_text = f"{drive.device} - {drive.size}{mount_info}"
            drive_list.append(ListItem(Label(label_text)))

        self.drives = drives

    def get_usb_drives(self) -> List[DriveInfo]:
        """Get list of USB drives using lsblk"""
        try:
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,SIZE,TYPE,MOUNTPOINT,FSTYPE', '-n', '-l'],
                capture_output=True,
                text=True,
                check=True
            )

            # First pass: identify system disks (those with critical mount points)
            system_disks = set()
            lines = result.stdout.strip().split('\n')

            for line in lines:
                parts = line.split()
                if len(parts) < 3:
                    continue

                name = parts[0]
                mountpoint = ''

                if len(parts) > 3 and parts[3].startswith('/'):
                    mountpoint = parts[3]

                # If this partition has a critical mount point, mark its parent disk as system
                if mountpoint in ['/', '/boot', '/boot/efi', '/home', '/usr', '/var']:
                    # Extract base disk name (e.g., sda1 -> sda, nvme0n1p1 -> nvme0n1)
                    if 'nvme' in name or 'mmcblk' in name:
                        # Handle nvme0n1p1 -> nvme0n1, mmcblk0p1 -> mmcblk0
                        base_disk = name.rstrip('0123456789').rstrip('p')
                    else:
                        # Handle sda1 -> sda
                        base_disk = name.rstrip('0123456789')

                    system_disks.add(base_disk)

            # Second pass: collect drives that aren't system disks
            drives = []
            for line in lines:
                parts = line.split()
                if len(parts) < 3:
                    continue

                name = parts[0]
                size = parts[1]
                dtype = parts[2]
                mountpoint = ''
                fstype = ''

                if len(parts) > 3 and parts[3].startswith('/'):
                    mountpoint = parts[3]
                    fstype = parts[4] if len(parts) > 4 else ''
                else:
                    fstype = parts[3] if len(parts) > 3 else ''

                # Only include disk types (not partitions) and exclude loops
                if dtype == 'disk' and not name.startswith('loop'):
                    # Check if this disk or any of its prefixes are system disks
                    is_system_disk = any(name.startswith(sys_disk) for sys_disk in system_disks)

                    if not is_system_disk:
                        device = f"/dev/{name}"
                        drives.append(DriveInfo(device, size, mountpoint, fstype))

            return drives
        except subprocess.CalledProcessError as e:
            return []

    @on(ListView.Selected, "#drive_list")
    def on_drive_selected(self, event: ListView.Selected) -> None:
        """Handle drive selection"""
        selected_drive = self.drives[event.list_view.index]
        self.app.selected_drive = selected_drive
        self.app.push_screen(ConfirmationScreen())


class ConfirmationScreen(Screen):
    """Screen for confirming the operation with warnings"""

    BINDINGS = [
        Binding("escape", "app.pop_screen", "Back"),
        Binding("q", "app.quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        drive = self.app.selected_drive
        file = self.app.selected_file

        warning = ""
        if drive.size_gb > 10:
            warning = f"\n[bold red]⚠ WARNING: The selected drive is {drive.size}![/bold red]\n[red]This is larger than 10GB. Please verify this is correct.[/red]\n"

        yield Header()
        yield Container(
            Static("Confirm Operation", classes="title"),
            Static(f"\n[bold]File:[/bold] {file.name}"),
            Static(f"[bold]File size:[/bold] {self.format_size(file.stat().st_size)}"),
            Static(f"\n[bold]Target drive:[/bold] {drive.device}"),
            Static(f"[bold]Drive size:[/bold] {drive.size}"),
            Static(warning),
            Static("\n[bold yellow]⚠ This will erase ALL data on the selected drive![/bold yellow]"),
            Static("\nThe drive will be:"),
            Static("  1. Unmounted (if mounted)"),
            Static("  2. Formatted as FAT32"),
            Static("  3. The Juniper file will be copied"),
            Horizontal(
                Button("Cancel", variant="default", id="cancel_btn"),
                Button("Proceed", variant="error", id="proceed_btn"),
                classes="button-row"
            ),
            id="confirm_container"
        )
        yield Footer()

    def format_size(self, size_bytes: int) -> str:
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"

    @on(Button.Pressed, "#cancel_btn")
    def on_cancel(self) -> None:
        self.app.pop_screen()

    @on(Button.Pressed, "#proceed_btn")
    def on_proceed(self) -> None:
        self.app.push_screen(ProgressScreen())


class ProgressScreen(Screen):
    """Screen showing progress of the operation"""

    def compose(self) -> ComposeResult:
        yield Header()
        yield Container(
            Static("Processing...", classes="title"),
            Static("", id="status"),
            Static("", id="details"),
            Static("", id="result"),
            Button("Done", variant="primary", id="done_btn", disabled=True),
            id="progress_container"
        )
        yield Footer()

    def on_mount(self) -> None:
        """Start the operation when mounted"""
        self.perform_operation()

    def perform_operation(self) -> None:
        """Perform the format and copy operation"""
        status = self.query_one("#status", Static)
        details = self.query_one("#details", Static)
        result_widget = self.query_one("#result", Static)
        done_btn = self.query_one("#done_btn", Button)

        drive = self.app.selected_drive
        file = self.app.selected_file

        try:
            # Step 1: Unmount if mounted (including all partitions)
            status.update("[bold]Step 1/3:[/bold] Unmounting drive...")

            # Get all mounted partitions for this device
            result = subprocess.run(
                ['lsblk', '-o', 'NAME,MOUNTPOINT', '-n', '-l'],
                capture_output=True,
                text=True,
                check=True
            )

            # Extract device name without /dev/
            device_name = drive.device.replace('/dev/', '')
            unmounted_any = False

            # Find and unmount all partitions
            for line in result.stdout.strip().split('\n'):
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    mountpoint = parts[1] if len(parts) > 1 else ''

                    # Check if this is a partition of our device
                    if name.startswith(device_name) and mountpoint:
                        details.update(f"Unmounting {mountpoint}...")
                        umount_result = subprocess.run(
                            ['sudo', 'umount', f'/dev/{name}'],
                            capture_output=True,
                            text=True
                        )
                        if umount_result.returncode != 0:
                            raise Exception(f"Failed to unmount /dev/{name}: {umount_result.stderr}")
                        details.update(f"✓ Unmounted /dev/{name}")
                        unmounted_any = True

            if not unmounted_any:
                details.update("✓ Drive not mounted")

            # Step 2: Format as FAT32
            status.update("[bold]Step 2/3:[/bold] Formatting as FAT32...")
            details.update(f"Formatting {drive.device}...")
            result = subprocess.run(
                ['sudo', 'mkfs.vfat', '-F', '32', '-I', '-n', 'JUNIPER', drive.device],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Failed to format: {result.stderr}")
            details.update(f"✓ Formatted {drive.device} as FAT32")

            # Step 3: Mount and copy file
            status.update("[bold]Step 3/3:[/bold] Copying file...")

            # Create temporary mount point
            mount_point = "/tmp/juniper_usb_temp"
            os.makedirs(mount_point, exist_ok=True)

            details.update(f"Mounting {drive.device}...")
            result = subprocess.run(
                ['sudo', 'mount', drive.device, mount_point],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                raise Exception(f"Failed to mount: {result.stderr}")

            details.update(f"Copying {file.name}...")

            # Copy the file
            dest_path = os.path.join(mount_point, file.name)
            result = subprocess.run(
                ['sudo', 'cp', str(file), dest_path],
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                subprocess.run(['sudo', 'umount', mount_point], capture_output=True)
                raise Exception(f"Failed to copy file: {result.stderr}")

            # Sync to ensure data is written
            details.update("Syncing data...")
            subprocess.run(['sync'], check=True)

            # Unmount
            details.update("Unmounting...")
            subprocess.run(['sudo', 'umount', mount_point], check=True)

            # Clean up
            os.rmdir(mount_point)

            status.update("[bold green]✓ Operation completed successfully![/bold green]")
            details.update("")
            result_widget.update(
                f"\n[green]The USB drive is ready to use with your Juniper switch.[/green]\n"
                f"File: {file.name}\n"
                f"Drive: {drive.device}\n"
            )

        except Exception as e:
            status.update("[bold red]✗ Operation failed![/bold red]")
            details.update("")
            result_widget.update(f"\n[red]Error: {str(e)}[/red]\n")

        finally:
            done_btn.disabled = False

    @on(Button.Pressed, "#done_btn")
    def on_done(self) -> None:
        self.app.exit()


class JuniperWizardApp(App):
    """Main application"""

    CSS = """
    Screen {
        align: center middle;
    }

    #file_container, #drive_container, #confirm_container, #progress_container {
        width: 80;
        height: auto;
        border: solid green;
        padding: 1 2;
    }

    .title {
        width: 100%;
        content-align: center middle;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    .info {
        margin-bottom: 1;
        color: $text;
    }

    .help-text {
        margin-top: 1;
        content-align: center middle;
    }

    ListView {
        height: auto;
        max-height: 15;
        margin: 1 0;
        border: solid $primary;
    }

    .button-row {
        width: 100%;
        height: auto;
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("q", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self.selected_file: Optional[Path] = None
        self.selected_drive: Optional[DriveInfo] = None

    def on_mount(self) -> None:
        """Initialize the app"""
        self.title = "Juniper USB Wizard"
        self.sub_title = "Format USB drives for Juniper switches"

        # Get list of Juniper files
        files_dir = Path(__file__).parent / "juniper_files"
        juniper_files = list(files_dir.glob("*.tgz"))

        if not juniper_files:
            self.exit(message="Error: No Juniper files found in juniper_files directory")
            return

        # Push the file selection screen
        self.push_screen(FileSelectionScreen(juniper_files))


def main():
    """Entry point"""
    # Check if running as root or with sudo access
    if os.geteuid() != 0:
        # Check if sudo is available
        result = subprocess.run(['sudo', '-n', 'true'], capture_output=True)
        if result.returncode != 0:
            print("Error: This program requires sudo access to format drives.")
            print("Please run: sudo -v")
            print("Then run the program again.")
            sys.exit(1)

    app = JuniperWizardApp()
    app.run()


if __name__ == "__main__":
    main()
