import asyncio
import logging
import signal
from core.server import serve
from dotenv import load_dotenv

load_dotenv()

SERVICE_NAME = "service-dashboard-hypnos"
GRPC_SERVER_HOST = "[::1]"
GRPC_SERVER_PORT = 50051


async def shutdown(server, loop):
    logging.info("application stopped.")
    await server.stop(5)
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    [task.cancel() for task in tasks]
    await asyncio.gather(*tasks, return_exceptions=True)
    loop.stop()


async def main():
    loop = asyncio.get_running_loop()

    server = await serve(GRPC_SERVER_HOST, GRPC_SERVER_PORT)

    logging.info(f"{SERVICE_NAME}")
    logging.info(f"server listening at http://[::1]:{GRPC_SERVER_PORT}")
    logging.info(f"server listening at http://127.0.0.1:{GRPC_SERVER_PORT}")
    logging.info(f"grpc server started.")

    shutdown_event = asyncio.Event()

    def signal_handler():
        shutdown_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            signal.signal(sig, lambda s, f: signal_handler())

    try:
        await shutdown_event.wait()
    finally:
        await shutdown(server, loop)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
