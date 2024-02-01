
from argparse import ArgumentParser

ASSIGNMENT_ID = 'ex02b'
todo = {}

def _get_arguments():
    parser = ArgumentParser(
        description=ASSIGNMENT_ID
    )
    parser.add_argument(
        '-r', '--review', choices=['0', '1', '2'], default='0',
        help='whose code is being run, default: 0 (your code)'
    ) 
    return vars(parser.parse_args())

def _get_todo_folder(args):
    return 'your_code' if not int(args.get('review')) else f'review_{args["review"]}'     

def set_config():
    args = _get_arguments()
    todo['folder'] = _get_todo_folder(args)
    todo['prompt'] = f'{ASSIGNMENT_ID} [{todo["folder"]}] > '
