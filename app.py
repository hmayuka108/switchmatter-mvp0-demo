
"""SwitchMatter Streamlit entry point."""

import sys
from pathlib import Path

# Add the local src directory to Python's module search path.
ROOT_DIR = Path(__file__).resolve().parent
SRC_DIR = ROOT_DIR / "src"

if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from switchmatter.streamlit_ui import main

if __name__ == "__main__":
    main()
