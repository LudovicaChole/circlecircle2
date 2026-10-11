# LS-DYNA text editing

Opening a `.k` or `.key` file automatically enables the LS-DYNA editor view.
The view uses a fixed-width font, line numbers, alternating field backgrounds,
and dotted boundaries on data cards. The ruler above the text follows the cursor
and shows the current keyword, field names, column ranges, line and column.
These marks are display aids: they are never inserted into the file.

Field widths depend on the keyword and card. For example:

| Card | Standard field widths (characters) |
| --- | --- |
| `*NODE` | 8, 16, 16, 16, 8, 8 |
| `*ELEMENT_SHELL` connectivity | 8 per field |
| `*ELEMENT_MASS` | 8, 8, 16, 8 |
| `*PART` numeric card | 10 per field |
| `*DEFINE_CURVE` header | 10 per field |
| `*DEFINE_CURVE` points | 20 per field |

The initial layout catalog includes these cards, basic solid connectivity,
shell thickness cards, selected sets, contacts, controls, database output cards,
sections and materials. Comments and title lines do not receive numeric guides.
Comma-separated data uses the actual comma boundaries instead of fixed columns.
Generic field labels such as F1 indicate positions without a named field label.

Only standard short-format guides are supported. Declared I10 and long formats
show an unsupported-format notice. Unverified keywords/options and data lines
containing tabs do not receive fixed-column guides. This editor does not validate
solver input or automatically pad, truncate or reformat data. Formats selected
only through an external solver command line cannot be detected from file text.

Layouts follow the local LS-DYNA R13 Keyword User's Manual, Volume I:
Getting Started 2-27 through 2-30; NODE 33-2; ELEMENT 19-60,
19-95 through 19-97 and 19-115 through 19-118; DEFINE 17-84,
17-85 and 17-369; PART 35-4 and 35-5; SET 41-37 and 41-61.
Material cards are described in Volume II.
Official manuals: https://www.dynasupport.com/manuals/ls-dyna-manuals
