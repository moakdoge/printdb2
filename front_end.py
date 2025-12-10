from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from aioconsole import ainput

manager.load_plugin_folder(f"{os.path.join(os.path.split(__file__)[0], "plugins")}")

async def main():
    while True:
        try:
            content = await ainput(input_prompt.input_prompt())
        except KeyboardInterrupt:
            for t in manager._tasks:
                t.cancel()
            break
        await manager.run(content)

try:
    asyncio.run(main())
except KeyboardInterrupt:
    pass