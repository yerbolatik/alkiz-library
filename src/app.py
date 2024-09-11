import asyncio
import logging
import uvicorn

from app.asgi import application as web_application
from tg_bot.bot import get_application


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def main() -> None:
    """Finalize configuration and run the applications."""
    application = await get_application()
    web_application.tg_application = application
    webserver = uvicorn.Server(
        config=uvicorn.Config(
            app=web_application,
            port=8001,
            use_colors=False,
            host="127.0.0.1",
        )
    )

    async with application:
        # Run application and webserver together
        await application.start()
        await webserver.serve()
        await application.stop()

if __name__ == "__main__":
    asyncio.run(main())
