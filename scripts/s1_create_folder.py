import os

# Define the root directory and the range of folder names
# root_directory = r"E:\LYZ\AucklandCourse\2024Thesis\Thesis\VIGIL-ReID\data\CatIndividualImages\IDs"
root_directory = r"F:\archive\data\CowDataset\IDs"
start_number = 0
end_number = 12

# Create folders
for i in range(start_number, end_number + 1):
    folder_path = os.path.join(root_directory, str(i))
    os.makedirs(folder_path, exist_ok=True)

print(f"Successfully created folders from {start_number} to {end_number} in {root_directory}.")