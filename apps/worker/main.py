"""Worker process entrypoint."""
import asyncio
from apps.worker.scheduler import WorkerScheduler
async def main(): await WorkerScheduler().run_once()
if __name__=="__main__": asyncio.run(main())
