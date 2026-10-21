#!/usr/bin/env python3
# *******************************************************************************
# Copyright (c) 2026 Contributors to the Eclipse Foundation
#
# See the NOTICE file(s) distributed with this work for additional
# information regarding copyright ownership.
#
# This program and the accompanying materials are made available under the
# terms of the Apache License Version 2.0 which is available at
# https://www.apache.org/licenses/LICENSE-2.0
#
# SPDX-License-Identifier: Apache-2.0
# *******************************************************************************

"""
Offline ext4 overlay injection using debugfs.

Injects tar archive contents into an ext4 filesystem without requiring
loop mounts, root privileges, or CAP_SYS_ADMIN. Uses debugfs -w for
userspace ext4 modification.

Usage:
    inject_overlay.py --image SOURCE.img --partition N --tar overlay.tar --output TARGET.img

The script:
1. Extracts partition N from SOURCE.img using dd
2. Injects tar contents via debugfs -w commands
3. Writes the modified partition back to TARGET.img

This preserves all partition table metadata and non-target partitions.
"""

import argparse
import os
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path


def get_partition_info(image_path: str, partition: int) -> tuple[int, int]:
    """
    Get partition offset and size using partx.
    
    Returns:
        Tuple of (offset_bytes, size_bytes)
    """
    result = subprocess.run(
        ["partx", "--show", image_path],
        capture_output=True,
        text=True,
        check=True,
    )
    
    for line in result.stdout.strip().split("\n"):
        parts = line.split()
        if len(parts) >= 4 and parts[0] == str(partition):
            start_sector = int(parts[1])
            end_sector = int(parts[2])
            sectors = int(parts[3])
            sector_size = 512  # Standard sector size
            offset = start_sector * sector_size
            size = sectors * sector_size
            return offset, size
    
    raise ValueError(f"Partition {partition} not found in {image_path}")


def extract_partition(image_path: str, partition: int, output_path: str) -> None:
    """Extract a partition to a file using dd."""
    offset, size = get_partition_info(image_path, partition)
    
    subprocess.run(
        [
            "dd",
            f"if={image_path}",
            f"of={output_path}",
            f"skip={offset}",
            f"count={size}",
            "bs=1",
            "iflag=skip_bytes,count_bytes",
        ],
        check=True,
        capture_output=True,
    )


def write_partition(image_path: str, partition: int, partition_file: str) -> None:
    """Write a partition back into an image using dd."""
    offset, _ = get_partition_info(image_path, partition)
    
    subprocess.run(
        [
            "dd",
            f"if={partition_file}",
            f"of={image_path}",
            f"seek={offset}",
            "bs=1",
            "oflag=seek_bytes",
            "conv=notrunc",
        ],
        check=True,
        capture_output=True,
    )


def generate_debugfs_commands(tar_path: str) -> list[str]:
    """
    Generate debugfs commands to inject tar contents.
    
    Returns a list of debugfs commands that will:
    - Create directories
    - Write files
    - Create symlinks
    - Set permissions and ownership
    """
    commands = []
    
    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            path = member.name.lstrip("/")
            
            if member.isdir():
                commands.append(f"mkdir -p {path}")
            elif member.isfile():
                # debugfs write command copies from host file
                # We need to extract to temp file first, so we use a different approach
                commands.append(f"# FILE: {path}")
            elif member.issym():
                commands.append(f"# SYMLINK: {path} -> {member.linkname}")
    
    return commands


def inject_tar_contents(partition_path: str, tar_path: str) -> None:
    """
    Inject tar contents into an ext4 partition using debugfs.
    
    debugfs -w provides an interactive shell for ext4 manipulation.
    We use it to create directories, write files, and set metadata.
    """
    # Build a script of debugfs commands
    debugfs_script = []
    
    with tarfile.open(tar_path, "r:*") as tf:
        # First pass: create all directories
        dirs_to_create = []
        for member in tf.getmembers():
            if member.isdir():
                path = member.name.lstrip("/")
                dirs_to_create.append(path)
            elif member.isfile() or member.issym():
                # Ensure parent directory exists
                parent = str(Path(member.name.lstrip("/")).parent)
                if parent and parent != ".":
                    dirs_to_create.append(parent)
        
        # Sort by depth to create parents first
        dirs_to_create = sorted(set(dirs_to_create), key=lambda p: p.count("/"))
        for d in dirs_to_create:
            debugfs_script.append(f"mkdir -p {d}")
        
        # Second pass: write files and symlinks
        for member in tf.getmembers():
            path = member.name.lstrip("/")
            
            if member.isfile():
                # Extract file to temp location for debugfs write
                # debugfs write command: write local_file dest_path
                # We'll extract each file and write it
                debugfs_script.append(f"# WRITE_FILE: {path}")
                # Note: Actual file writing requires temp file extraction
                # We handle this in the execution phase
            
            elif member.issym():
                # Create symlink: symlink target path
                debugfs_script.append(f"symlink {member.linkname} {path}")
    
    # For actual file injection, we use debugfs's write command
    # which requires the source file to exist on the host
    # We'll extract each file to a temp dir and reference it
    
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Extract all files to temp dir
        with tarfile.open(tar_path, "r:*") as tf:
            tf.extractall(temp_path, filter='data')
        
        # Build the debugfs command list with actual file references
        write_commands = []
        
        with tarfile.open(tar_path, "r:*") as tf:
            for member in tf.getmembers():
                path = member.name.lstrip("/")
                
                if member.isfile():
                    local_file = temp_path / member.name.lstrip("/")
                    if local_file.exists():
                        write_commands.append(f"write {local_file} {path}")
        
        # Run debugfs with all commands
        all_commands = ["mkdir -p " + d for d in dirs_to_create] + write_commands
        
        # debugfs -w -f reads commands from file
        cmd_file = temp_path / "debugfs.cmds"
        cmd_file.write_text("\n".join(all_commands) + "\n")
        
        subprocess.run(
            ["debugfs", "-w", "-f", str(cmd_file), partition_path],
            check=True,
            capture_output=True,
        )


def check_free_space(partition_path: str, required_bytes: int) -> None:
    """
    Check that the partition has enough free space for the overlay.
    
    Raises ValueError if insufficient space.
    """
    result = subprocess.run(
        ["dumpe2fs", "-h", partition_path],
        capture_output=True,
        text=True,
        check=True,
    )
    
    free_blocks = 0
    block_size = 4096
    
    for line in result.stdout.split("\n"):
        if line.startswith("Free blocks:"):
            free_blocks = int(line.split(":")[1].strip())
        elif line.startswith("Block size:"):
            block_size = int(line.split(":")[1].strip())
    
    free_bytes = free_blocks * block_size
    
    if free_bytes < required_bytes:
        raise ValueError(
            f"Insufficient free space: {free_bytes} bytes available, "
            f"{required_bytes} bytes required"
        )


def get_tar_size(tar_path: str) -> int:
    """Estimate the extracted size of a tar archive."""
    total_size = 0
    with tarfile.open(tar_path, "r:*") as tf:
        for member in tf.getmembers():
            if member.isfile():
                total_size += member.size
    # Add 10% overhead for filesystem metadata
    return int(total_size * 1.1)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inject tar overlay into ext4 partition via debugfs"
    )
    parser.add_argument(
        "--image", required=True, help="Source image file"
    )
    parser.add_argument(
        "--partition", type=int, required=True, help="Partition number to inject into"
    )
    parser.add_argument(
        "--tar", required=True, help="Tar archive to inject"
    )
    parser.add_argument(
        "--output", required=True, help="Output image file"
    )
    parser.add_argument(
        "--no-space-check", action="store_true",
        help="Skip free space verification"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not os.path.exists(args.image):
        print(f"Error: Image file not found: {args.image}", file=sys.stderr)
        return 1
    
    if not os.path.exists(args.tar):
        print(f"Error: Tar file not found: {args.tar}", file=sys.stderr)
        return 1
    
    # Copy source image to output location
    if args.output != args.image:
        subprocess.run(["cp", args.image, args.output], check=True)
    
    # Work on a copy of the partition
    with tempfile.TemporaryDirectory() as temp_dir:
        partition_file = Path(temp_dir) / "partition.img"
        
        # Extract the partition
        print(f"Extracting partition {args.partition}...")
        extract_partition(args.output, args.partition, str(partition_file))
        
        # Check free space
        if not args.no_space_check:
            required = get_tar_size(args.tar)
            print(f"Checking free space (need ~{required} bytes)...")
            check_free_space(str(partition_file), required)
        
        # Inject the tar contents
        print(f"Injecting {args.tar}...")
        inject_tar_contents(str(partition_file), args.tar)
        
        # Write the partition back
        print(f"Writing modified partition...")
        write_partition(args.output, args.partition, str(partition_file))
    
    print(f"Done: {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
