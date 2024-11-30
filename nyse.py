import kagglehub

# Download latest version
path = kagglehub.dataset_download("dgawlik/nyse")

print("Path to dataset files:", path)