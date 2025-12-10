from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from aioconsole import ainput

manager.load_plugin_folder(f"{os.path.join(os.path.split(__file__)[0], "plugins")}")

async def main():
    while True:
        try:
            content = await asyncio.to_thread(input, input_prompt.input_prompt())
            await asyncio.shield(manager.run(content))
        except (asyncio.exceptions.CancelledError, EOFError):
            stop = await manager.stop()
            if stop:
                continue
            await manager.stop_all()


try:
    asyncio.run(main())
except (KeyboardInterrupt,EOFError):
    pass