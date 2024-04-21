import asyncio
from dotenv import load_dotenv


load_dotenv()

# from database.utils import create_all_tables
from main_app.scripts import main_script


if __name__ == "__main__":
    bets = asyncio.run(main_script())
