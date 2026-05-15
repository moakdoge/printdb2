from printdb.api import *
from printdb.api.logichelper import *

@manager.command(name="if", author="moakdoge")
async def _if(ctx: CommandContext, *statement: str):
    
    #first, strip () if it has them
    new = []
    for part in statement:
        _op = get_operand(part, "", "")
        if _op is not None:
            new.append(_op)
            continue
        
        if part[0] == "(" and part[-1] == ")":
            part = part[1:-1]
        
        new.append(part)
    
    await ctx.pprint(" ".join(new))