from pathlib import Path

import payne

# Paths
payne_project = Path(payne.__file__).parent.parent.parent
test_data = payne_project / "test_data"
run = payne_project / "run"
test_data_index = run / "payne_test_data"

# Test data index URLs
test_data_index_url_server = "http://localhost:8000/payne_test_data"
test_data_index_url_files = f"file://{test_data_index.absolute().as_posix()}"
