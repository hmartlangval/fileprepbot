import sys
import importlib
from pathlib import Path
from dotenv import load_dotenv

def setup_path():
    """Add project root to Python path for relative imports"""
    project_root = str(Path(__file__).parent)
    if project_root not in sys.path:
        sys.path.append(project_root)

def load_env(bot_name):
    """Load environment variables"""
    project_root = Path(__file__).parent
    # Load root .env first
    load_dotenv(project_root / '.env')
    # Then load bot-specific .env
    load_dotenv(project_root / bot_name / '.env', override=True)

def run_bot(bot_name):
    """Run the run.py file of the specified bot"""
    load_env(bot_name)
    importlib.import_module(f"{bot_name}.run")

def main():
    setup_path()
    bot_name = sys.argv[1]
    run_bot(bot_name)

if __name__ == '__main__':
    main() 