from pathlib import Path

import payne

test_data = Path(payne.__file__).parent.parent.parent / "test_data"
run = Path(payne.__file__).parent.parent.parent / "run"
test_data_index = run / "payne_test_data"

test_data_index_url="http://localhost:8000/payne_test_data"
