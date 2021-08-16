# importing module
import sys

import click
from telegram.ext import Dispatcher

# appending a path
sys.path.append('../g3b1_tgdata')

from g3b1_test import test_utils
from g3b1_serv import utilities

# # importing sys
# import sys
#
# # adding Folder_2 to the system path
# sys.path.insert(0, r'C:\Users\IFLRGU\PycharmProjects\g3b1_data')

dispatcher: Dispatcher = test_utils.setup(todo_main.file_name())


@click.command()
@click.option("--title", prompt="Title", help="Title of todo")
def cli(title):
    ts = test_utils.TestSuite(dispatcher, [])
    tc = test_utils.TestCaseHdl(utilities.g3_cmd_by_func(
        todo_main.hdl_cmd_create),
        {'title': title}
    )
    ts.tc_exec(tc)


def main():
    cli()


if __name__ == '__main__':
    main()
