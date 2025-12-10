from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline,os,asyncio

manager.load_plugin_folder(f"{os.path.join(os.path.split(__file__)[0], "plugins")}")

async def main():
    while True:
        content = input(input_prompt.input_prompt())
        output = await manager.run(content)
        if output.error_code != ErrorCode.SUCCESS:
            print(input_prompt.error(output))

asyncio.run(main())