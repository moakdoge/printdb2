from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer, colorize, input_prompt
import readline

manager.load_plugin_folder("/home/moakdoge/Desktop/printdb2-1/plugins")

while True:
    content = input(input_prompt.input_prompt())
    cmd, args = tokenizer.tokenize_args(content)
    output = manager.run(cmd, args)
    if output.error_code != ErrorCode.SUCCESS:
        print(input_prompt.error(output))
