import dash_bootstrap_components as dbc

def navbar():
    return dbc.Nav(
        [
            dbc.NavItem(dbc.NavLink("Status", active=True, href="#")),
            dbc.NavItem(dbc.NavLink("Stats", href="#")),
        ], pills=True
    )
# navbar=None
