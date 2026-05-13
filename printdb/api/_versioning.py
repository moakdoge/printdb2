from pathlib import Path


def _get_version(default: int = 0) -> int:
    '''Gets version.'''
    
    #__init__.py, for overloading
    INIT = Path(__file__).parent.parent / "__init__.py"
    try:
        contents = INIT.read_text()
        l = [_.replace(" ", "") for _ in contents.splitlines() if _.startswith("#version:")][0].removeprefix("#version:")
        return int(l)
    except Exception as e:
        pass

    
    #git, most reliable method
    try:
        import subprocess

        count = int(subprocess.check_output([
            "git",
            "rev-list",
            "--count",
            "HEAD"
        ]).strip())

        return int(count)
    except Exception as e:
        pass
    

    #fallback
    return default