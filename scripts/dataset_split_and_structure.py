import os
import shutil
import argparse
import random

EXTENSIONS = ["jpeg", "png", "jpg"]

def split_dataset(input_dir, output_dir, split_ratio, val_ratio=None):
    random.seed(42)  # Ensures reproducibility

    # Check if output directory is exists
    if not os.path.exists(output_dir):
        raise RuntimeError(f"\033[91mError: The output directory '{output_dir}' does not exist. Please ensure its creation.\033[0m")

    # Check if output directory is empty
    if os.path.exists(output_dir) and os.listdir(output_dir):
        raise RuntimeError(f"\033[91mError: The output directory '{output_dir}' is not empty. Please provide an empty directory.\033[0m")

    train_dir = os.path.join(output_dir, "train")
    test_dir = os.path.join(output_dir, "test")
    val_dir = os.path.join(output_dir, "val") if val_ratio else None

    # Create output directories
    for dir_path in [train_dir, test_dir, val_dir]:
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path)

    # Iterate through class folders
    for class_name in os.listdir(input_dir):
        class_path = os.path.join(input_dir, class_name)
        if not os.path.isdir(class_path):
            continue

        # Collect all file paths in the class folder
        file_paths = [os.path.join(class_path, file_name) for file_name in os.listdir(class_path)]
        valid_files = []

        for file_path in file_paths:
            if file_path.split(".")[-1].lower() in EXTENSIONS:
                valid_files.append(file_path)
            else:
                print(f"Warning: Skipping unsupported file type: {file_path}")

        random.shuffle(valid_files)

        # Calculate split indices
        total_files = len(valid_files)
        train_split_idx = int(total_files * split_ratio)
        val_split_idx = train_split_idx + int(total_files * val_ratio) if val_ratio else train_split_idx

        train_files = valid_files[:train_split_idx]
        test_files = valid_files[train_split_idx:val_split_idx]
        val_files = valid_files[val_split_idx:] if val_ratio else []

        # Copy files to respective directories
        for file_list, target_dir in [(train_files, train_dir), (test_files, test_dir), (val_files, val_dir)]:
            if not target_dir:
                continue
            target_class_dir = os.path.join(target_dir, class_name)
            os.makedirs(target_class_dir, exist_ok=True)
            for file_path in file_list:
                shutil.copy(file_path, target_class_dir)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split dataset into train, test, and optional val sets.")
    parser.add_argument("--input_dir", type=str, required=True, help="Path to the input dataset directory.")
    parser.add_argument("--output_dir", type=str, default="./", help="Path to the output directory.")
    parser.add_argument("--split_ratio", type=float, default=0.7, help="Proportion of data for training.")
    parser.add_argument("--val_ratio", type=float, default=0.15, help="Proportion of data for validation.")

    args = parser.parse_args()

    if args.val_ratio and args.split_ratio + args.val_ratio >= 1.0:
        raise ValueError("split_ratio and val_ratio must sum to less than 1.0")

    split_dataset(args.input_dir, args.output_dir, args.split_ratio, args.val_ratio)
