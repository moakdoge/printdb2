from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio
from aioconsole import ainput
import sys

manager.load_plugin_folder(f"{os.path.join(os.path.split(__file__)[0], "plugins")}")

ON_INPUT= False
async def main():
    await manager.stop()
    global ON_INPUT
    while True:
        if True:
            ON_INPUT = True
            content = await ainput(input_prompt.input_prompt())
            ON_INPUT = False
            await manager.run(content)



if __name__ == "__main__":

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    while True:
        try:
            loop.run_until_complete(main())
        except KeyboardInterrupt:
            if ON_INPUT:
                sys.exit(1)
                break
