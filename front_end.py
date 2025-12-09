from printdb.api import manager, ErrorCode
from printdb.api.frontend import tokenizer
manager.load_plugin_folder("/home/moakdoge/Desktop/printdb2-1/plugins")

while True:
    content = input(">")
    cmd, args = tokenizer.tokenize_args(content)
    output = manager.run(cmd, args)
    if output.error_code != ErrorCode.SUCCESS:
        print(f"[ERROR CODE {output.error_code.name} (Code {output.error_code})]: {output.output}")