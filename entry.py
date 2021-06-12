if __name__ == "__main__":
    import sys
    from manager import build_argparser
    from deploy import PythonDeployer

    arg_str = ' '.join(sys.argv[1:])
    args = build_argparser().parse_args()

    pyd = PythonDeployer(args.p)
    pyd(arg_str)