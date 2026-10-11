"""Keep OS-generated diagnostics in English even on a localized Windows system."""


def error_message(error):
    if isinstance(error, OSError):
        descriptions = {FileNotFoundError: 'File or folder not found',
                        PermissionError: 'Permission denied or file in use',
                        IsADirectoryError: 'Expected a file, but found a folder',
                        NotADirectoryError: 'Expected a folder',
                        FileExistsError: 'File or folder already exists'}
        message = descriptions.get(type(error), 'File system operation failed')
        code = getattr(error, 'winerror', None) or error.errno
        if code is not None:
            message += f' (system error {code})'
        if error.filename:
            message += f': {error.filename}'
        # Application-generated errors already contain actionable English guidance.
        if error.errno is None and error.args and isinstance(error.args[0], str):
            return error.args[0]
        return message
    return str(error)
