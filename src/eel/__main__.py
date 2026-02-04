def main():
    import sys
    from . import vm
    ARGS = list(ARG.lower() for ARG in sys.argv[1:])
    if not ARGS or '--help' in ARGS:
        print('[EELScript]\nVersion: 1.0.0\nCMD:\n\t\033[1m$\033[0m eel \033[3mpath\033[0m [--strict] [--var | --json | --both ] [--dict] | [--help]')
        return

    path = [arg for arg in ARGS if arg not in {'--var', '--help', '--strict', '--json', '--dict', '--load', '--both'}][0]

    if '--load' in ARGS:
            vm.BaseMachine.loads(path)
            return
    
    machine = vm.Machine(path)
    machine.load()
    res = machine.run(strict= '--strict' in ARGS,\
                dict_out='--dict' in ARGS, \
                json_fout='--json' in ARGS or '--both' in ARGS,\
                var_fout='--var' in ARGS or '--both' in ARGS)

    if '--sniff' in ARGS: machine.sniff(path)
    if '--dict' in ARGS: print(res)

if __name__ == "__main__":
    main()