import asyncio

from main_app.scripts import update_rows

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    asyncio.run(update_rows())
