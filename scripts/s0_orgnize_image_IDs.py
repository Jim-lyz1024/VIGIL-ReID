import pandas as pd
import os
import shutil
from pathlib import Path
from tqdm import tqdm

def organize_images_by_identity(metadata_path, base_image_dir, output_dir, target_species=None):
    """
    Organize images into folders named by identity based on metadata.csv
    
    Args:
        metadata_path: Path to metadata.csv file
        base_image_dir: Base directory containing the images folder
        output_dir: Output directory for organized images
        target_species: List of target species to process. If None, process all species.
                       Example: ['AAUZebraFish', 'AerialCattle2017']
    """
    # Read metadata.csv
    print("Reading metadata.csv...")
    df = pd.read_csv(metadata_path)
    
    print(f"Total records in metadata: {len(df)}")
    print(f"Unique identities: {df['identity'].nunique()}")
    print(f"Unique species: {df['species'].nunique()}")
    
    # Filter by target species if specified
    if target_species is not None:
        if isinstance(target_species, str):
            target_species = [target_species]
        
        # Filter by dataset column (which contains species like AAUZebraFish)
        df = df[df['dataset'].isin(target_species)]
        print(f"\nFiltering for species: {target_species}")
        print(f"Records after filtering: {len(df)}")
        
        if len(df) == 0:
            print("Warning: No records found for specified species!")
            print("Available species in metadata:")
            print(pd.read_csv(metadata_path)['dataset'].unique())
            return
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Statistics
    success_count = 0
    failed_count = 0
    failed_files = []
    
    # Process each row
    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Processing images"):
        identity = row['identity']
        relative_path = row['path']
        
        # Build source file path
        source_path = os.path.join(base_image_dir, relative_path)
        
        # Create target folder (named by identity)
        target_folder = os.path.join(output_dir, identity)
        os.makedirs(target_folder, exist_ok=True)
        
        # Build target file path (keep original filename)
        filename = os.path.basename(relative_path)
        target_path = os.path.join(target_folder, filename)
        
        # Check if source file exists
        if os.path.exists(source_path):
            try:
                # Copy file
                shutil.copy2(source_path, target_path)
                success_count += 1
            except Exception as e:
                print(f"\nError copying {source_path}: {e}")
                failed_count += 1
                failed_files.append(source_path)
        else:
            print(f"\nSource file not found: {source_path}")
            failed_count += 1
            failed_files.append(source_path)
    
    # Print statistics
    print("\n" + "="*60)
    print("Processing Complete!")
    print("="*60)
    print(f"Successfully copied: {success_count} files")
    print(f"Failed: {failed_count} files")
    print(f"Total identities created: {len(os.listdir(output_dir))}")
    
    if failed_files:
        print("\nFailed files:")
        for f in failed_files[:10]:  # Show first 10 only
            print(f"  - {f}")
        if len(failed_files) > 10:
            print(f"  ... and {len(failed_files) - 10} more")
    
    # Show file count per identity
    print("\nFiles per identity (top 10):")
    identity_counts = {}
    for identity_folder in os.listdir(output_dir):
        folder_path = os.path.join(output_dir, identity_folder)
        if os.path.isdir(folder_path):
            count = len(os.listdir(folder_path))
            identity_counts[identity_folder] = count
    
    # Sort by file count and display
    for identity, count in sorted(identity_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  {identity}: {count} images")


def list_available_species(metadata_path):
    """
    List all available species in the metadata file
    
    Args:
        metadata_path: Path to metadata.csv file
    """
    df = pd.read_csv(metadata_path)
    print("\nAvailable species in metadata:")
    print("="*60)
    species_counts = df['dataset'].value_counts()
    for species, count in species_counts.items():
        print(f"  {species}: {count} images")
    print("="*60)


if __name__ == "__main__":
    # Configuration
    metadata_path = "F:/archive/metadata_new.csv"
    base_image_dir = "F:/archive"  # Base directory containing images folder
    output_dir = "F:/archive/organized_by_identity"  # Output directory
    
    # ==========================================
    # Option 1: List all available species first
    # ==========================================
    # Uncomment the line below to see all available species
    # list_available_species(metadata_path)
    # exit(0)
    
    # ==========================================
    # Option 2: Process specific species
    # ==========================================
    # Specify target species (can be a list or a single string)
    # target_species = ['AAUZebraFish']  # Process only AAUZebraFish
    target_species = ['ZindiTurtleRecall']  # Process only ZindiTurtleRecall
    # target_species = ['AAUZebraFish', 'AerialCattle2017']  # Process multiple species
    # target_species = None  # Process all species
    
    # Check if metadata file exists
    if not os.path.exists(metadata_path):
        print(f"Error: metadata.csv not found at {metadata_path}")
        exit(1)
    
    # Execute organization
    organize_images_by_identity(
        metadata_path=metadata_path,
        base_image_dir=base_image_dir,
        output_dir=output_dir,
        target_species=target_species
    )
    
    print("\nDone! Check the output directory:")
    print(output_dir)