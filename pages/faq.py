import dash
import dash_mantine_components as dmc

dash.register_page(__name__, path='/faq', name='FAQ', title='tab title',
                   description="""google blurb description""") # '/' is home page

# ------------------------------------------------ Page Layout --------------------------------------------------------
layout = dmc.Box([
    dmc.Accordion(
        multiple=True,
        chevronPosition="left",
        variant="separated",
        children=[
            dmc.AccordionItem(
                [
                    dmc.AccordionControl("How do you get you keyword search volumes?"),
                    dmc.AccordionPanel(
                        "Our keyword search volumes are sourced from directly Google's Keyword Planner tool. "
                        "We utilise third party tools to collect this data."
                    ),
                ],
                value="Q1",
            ),
            dmc.AccordionItem(
                [
                    dmc.AccordionControl("Why is the previous month's Google keyword search volume still projected?"),
                    dmc.AccordionPanel(
                        "We source our data from Google’s Keyword Planner. Google typically updates keyword data "
                        "around the middle of the following month. As a result, there are times when the month has "
                        "ended but the data is not yet available. In such cases, we estimate the search volume for "
                        "that month using Google Trends data."
                    ),
                ],
                value="Q2",
            ),
            dmc.AccordionItem(
                [
                    dmc.AccordionControl("How do you get you Tiktok views?"),
                    dmc.AccordionPanel(
                        "Our Tiktok views are sourced from directly Tiktok's Creative Center. We interpolate the "
                        "interest over time Tiktok provides with the total views over that period. "
                        "We utilise third party tools to collect this data."
                    ),
                ],
                value="Q3",
            ),
            dmc.AccordionItem(
                [
                    dmc.AccordionControl("How often do you update the data?"),
                    dmc.AccordionPanel(
                        "We update our data on a weekly basis"
                    ),
                ],
                value="Q4",
            ),
        ],
    )
])