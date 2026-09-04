"""Background task scheduler abstraction."""
class WorkerScheduler:
    def __init__(self): self.jobs=[]
    def register(self,job): self.jobs.append(job)
    async def run_once(self):
        results=[]
        for job in self.jobs: results.append(await job())
        return results
