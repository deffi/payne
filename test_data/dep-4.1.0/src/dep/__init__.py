import importlib.metadata

def hello_dep():
    print("This is dep 4.1.0")
    pygments_version = importlib.metadata.version("pygments")
    print(f"This is pygments {pygments_version}")
