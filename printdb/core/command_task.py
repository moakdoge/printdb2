from .command import Command
from .context import CommandContext
import asyncio
import time
class CommandTask:
    def __init__(self, command: Command, context: CommandContext, task: asyncio.Task):
        self.command = command
        self.ctx = context
        self.task: asyncio.Task = task
        self._start_time = time.time_ns()
    
    @property
    def complete(self) -> bool:
        if self.task.done():
            return True
        return False
    
    @property
    def runtime(self) -> float:
        return (time.time_ns() - self._start_time) / 1e+9
    
    @property
    def running(self) -> bool:
        return not self.task.done()


    def stop(self):
        '''Gracefully attempts to stop the task.'''
        self.task.cancel()
    
    async def join(self):
        '''Waits for the task.'''
        await self.task