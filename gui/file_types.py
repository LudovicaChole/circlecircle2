"""Extensions shared by the tree, creation dialog, editor, and translator."""
SOURCE_SOLVERS = {
    '.inp': ('abaqus', '6.14'), '.geo': ('abaqus', '6.14'),
    '.k': ('lsdyna', '12.0'), '.key': ('lsdyna', '12.0'),
    '.pc': ('pamcrash', '2020'), '.inc': ('pamcrash', '2020'),
}
TEXT_EXTENSIONS = tuple(SOURCE_SOLVERS) + ('.txt', '.py', '.md', '.json', '.log', '.msg', '.sta', '.dat')
MEDIA_EXTENSIONS = ('.jpg', '.jpeg', '.gif', '.png')
TEXT_FILTER = 'Supported text files (' + ' '.join('*' + ext for ext in TEXT_EXTENSIONS) + ');;All files (*)'
TARGET_VERSIONS = {'ABAQUS': ('6.14', '2024'), 'Ls-Dyna': ('12.0', '13.0', '16.0'), 'PamCrash': ('2020', '2023')}
