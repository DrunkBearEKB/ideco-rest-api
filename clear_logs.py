import os


def main():
    path_to_logs = os.path.join(os.path.dirname(__file__), 'logs')
    answer_delete = input(
        f'Is this the correct directory to delete the logs in: '
        f'{path_to_logs}? (y/n) ')
    if answer_delete[0].lower() != 'y':
        return

    list_files_deleted = []
    list_files_not_deleted = []
    for path in os.listdir(path_to_logs):
        if path.startswith('logfile_') and path.endswith('.log'):
            try:
                os.remove(os.path.join(path_to_logs, path))
                list_files_deleted.append(os.path.join(path_to_logs, path))
            except OSError:
                list_files_not_deleted.append(os.path.join(path_to_logs, path))

    if len(list_files_deleted) != 0:
        print('DELETED LOG FILES:\n\t' +
              '\n\t'.join(list_files_deleted))
    else:
        print('DELETED LOG FILES:\n\t<empty>')

    if len(list_files_not_deleted) != 0:
        print('NOT DELETED LOG FILES DUE TO SOME ERROR:\n\t' +
              '\n\t'.join(list_files_not_deleted))


if __name__ == '__main__':
    main()
