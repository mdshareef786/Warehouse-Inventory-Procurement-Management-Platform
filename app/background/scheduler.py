import asyncio

from app.background.tasks import (
    cleanup_expired_refresh_tokens,
)

from app.core.logger import logger


_scheduler_task: asyncio.Task | None = None


async def background_scheduler():
    """
    Application-level background scheduler.

    Runs maintenance jobs periodically.
    """

    logger.info(
        "Background scheduler started"
    )

    while True:

        try:

            # -------------------------------------------------
            # Refresh token cleanup
            # -------------------------------------------------

            await asyncio.to_thread(
                cleanup_expired_refresh_tokens
            )

        except asyncio.CancelledError:

            logger.info(
                "Background scheduler stopped"
            )

            raise

        except Exception:

            logger.exception(
                "Background scheduler iteration failed"
            )

        # -----------------------------------------------------
        # Run again after 1 hour
        # -----------------------------------------------------

        await asyncio.sleep(
            60 * 60
        )


def start_background_scheduler():

    global _scheduler_task

    if (
        _scheduler_task is None
        or _scheduler_task.done()
    ):

        _scheduler_task = asyncio.create_task(
            background_scheduler()
        )

        logger.info(
            "Background scheduler task created"
        )


async def stop_background_scheduler():

    global _scheduler_task

    if _scheduler_task is not None:

        _scheduler_task.cancel()

        try:

            await _scheduler_task

        except asyncio.CancelledError:

            pass

        _scheduler_task = None

        logger.info(
            "Background scheduler task stopped"
        )