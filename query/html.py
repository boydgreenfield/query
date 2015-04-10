# Don't have lots of HTML polluting the core.py file

# Styles/constants
WARNING_BACKGROUND_COLOR = "#F6DF9F"
WARNING_TEXT_COLOR = "#E18300"

# Messages
GETPASS_USE_WARNING = ("<p style='border: 1px solid %s; font-style: bold; text-align: center; "
                       "padding: 20px; background-color: %s; color: %s;'>"
                       "Please enter your password in the terminal from which "
                       "this IPython notebook was launched or pass a password "
                       "explicitly to QueryDb()</p>" %
                       (WARNING_TEXT_COLOR, WARNING_BACKGROUND_COLOR, WARNING_TEXT_COLOR))

QUERY_DB_ATTR_MSG = ("<em>You're using a rich interactive terminal. "
                     "Great! Just hit tab to see the tables and columns "
                     "of this database.<em>")


# Functions
def df_to_html(df, title, bold=False):
    if bold:
        style = 'font-weight: bold;'
    else:
        style = 'font-style: italic;'
    return ('<div style="max-height:500px; max-width: 750px; overflow: auto;">\n' +
            ('<p style="padding-left: 30px; %s">' % style) + title + '</p>' +
            df.to_html(show_dimensions=False, max_rows=None, max_cols=None) +
            '\n</div>')
