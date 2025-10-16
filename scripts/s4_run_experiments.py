import os
import subprocess
import sys
from datetime import datetime

# ============================================================================
# CONFIGURATION - Modify these variables to run different experiments
# ============================================================================

# Training configuration
GPU = 0  # GPU device ID
SEED = 42  # Random seed
ROOT = "F:/archive/data"  # Data root directory
OUTPUT_DIR = None  # If None, auto-generate based on dataset and model

# Advanced options (optional)
ADDITIONAL_ARGS = []  # Add any additional command line arguments here
# Example: ADDITIONAL_ARGS = ["--some-flag", "value"]

# ============================================================================
# PRESET CONFIGURATIONS - Uncomment to use
# ============================================================================

# # AAUZebraFish with CLIPZeroShot
# DATASET = "AAUZebraFish"
# SOURCE_DOMAINS = ["AAUZebraFish"]
# TARGET_DOMAINS = ["AAUZebraFish"]
# MODEL = "CLIPZeroShot"
# CONFIG_FILE = "config/clipzeroshot.yaml"

# # AAUZebraFish with SIGLIPZeroShot
# DATASET = "AAUZebraFish"
# SOURCE_DOMAINS = ["AAUZebraFish"]
# TARGET_DOMAINS = ["AAUZebraFish"]
# MODEL = "SIGLIPZeroShot"
# CONFIG_FILE = "config/siglipzeroshot.yaml"

# CatIndividualImages with SIGLIPZeroShot 
DATASET = "ZindiTurtleRecall"
SOURCE_DOMAINS = ["ZindiTurtleRecall"]
TARGET_DOMAINS = ["ZindiTurtleRecall"]
MODEL = "CLIPZeroShot"
CONFIG_FILE = "config/clipzeroshot.yaml"

# # AmvrakikosTurtles with CLIPZeroShot
# DATASET = "AmvrakikosTurtles"
# SOURCE_DOMAINS = ["AmvrakikosTurtles"]
# TARGET_DOMAINS = ["AmvrakikosTurtles"]
# MODEL = "CLIPZeroShot"
# CONFIG_FILE = "config/clipzeroshot.yaml"

# # AmvrakikosTurtles with SIGLIPZeroShot
# DATASET = "AmvrakikosTurtles"
# SOURCE_DOMAINS = ["AmvrakikosTurtles"]
# TARGET_DOMAINS = ["AmvrakikosTurtles"]
# MODEL = "SIGLIPZeroShot"
# CONFIG_FILE = "config/siglipzeroshot.yaml"

# # AmvrakikosTurtles with SIGLIPAdapter
# DATASET = "AmvrakikosTurtles"
# SOURCE_DOMAINS = ["AmvrakikosTurtles"]
# TARGET_DOMAINS = ["AmvrakikosTurtles"]
# MODEL = "SIGLIPAdapter"
# CONFIG_FILE = "config/siglipadapter.yaml"

# ============================================================================
# DO NOT MODIFY BELOW THIS LINE
# ============================================================================

def build_command():
    """Build the training command from configuration variables"""
    
    # Auto-generate output directory if not specified
    if OUTPUT_DIR is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = f"output/{DATASET}-{MODEL}-{timestamp}"
    else:
        output_dir = OUTPUT_DIR
    
    # Build base command
    cmd = [
        sys.executable,  # Use current Python interpreter
        "train.py",
        "--gpu", str(GPU),
        "--seed", str(SEED),
        "--root", ROOT,
        "--output-dir", output_dir,
        "--dataset", DATASET,
        "--source-domains", *SOURCE_DOMAINS,
        "--target-domains", *TARGET_DOMAINS,
        "--model", MODEL,
        "--model-config-file", CONFIG_FILE
    ]
    
    # Add additional arguments if specified
    if ADDITIONAL_ARGS:
        cmd.extend(ADDITIONAL_ARGS)
    
    return cmd, output_dir


def print_config():
    """Print current configuration"""
    print("=" * 80)
    print("EXPERIMENT CONFIGURATION")
    print("=" * 80)
    print(f"Dataset: {DATASET}")
    print(f"Source Domains: {SOURCE_DOMAINS}")
    print(f"Target Domains: {TARGET_DOMAINS}")
    print(f"Model: {MODEL}")
    print(f"Config File: {CONFIG_FILE}")
    print(f"GPU: {GPU}")
    print(f"Seed: {SEED}")
    print(f"Data Root: {ROOT}")
    print("=" * 80)


def run_experiment():
    """Run the training experiment"""
    
    # Print configuration
    print_config()
    
    # Build command
    cmd, output_dir = build_command()
    
    # Print command
    print("\nRunning command:")
    print(" ".join(cmd))
    print("\n" + "=" * 80)
    
    print("\n" + "=" * 80)
    print("STARTING TRAINING")
    print("=" * 80)
    print(f"Output directory: {output_dir}\n")
    
    # Run command
    try:
        subprocess.run(cmd, check=True)
        print("\n" + "=" * 80)
        print("Training completed successfully!")
        print(f"Results saved to: {output_dir}")
        print("=" * 80)
    except subprocess.CalledProcessError as e:
        print("\n" + "=" * 80)
        print(f" Training failed with error code {e.returncode}")
        print("=" * 80)
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n" + "=" * 80)
        print("Training interrupted by user")
        print("=" * 80)
        sys.exit(1)


if __name__ == "__main__":
    run_experiment()