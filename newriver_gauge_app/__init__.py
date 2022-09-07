# dependencies
# from flask import Flask, render_template, request, url_for
from flask import Flask, render_template, url_for
import json
import plotly

#-----------------------------------------------------------------------------
# App initialization

app = Flask(__name__)

#-----------------------------------------------------------------------------
# local modules
import gauge_utils

#-----------------------------------------------------------------------------
# VIEWS

@app.route('/')
def index():

    # create page items should retur a dictionary with an info message string
    # and two charts.
    page_items_dict = gauge_utils.create_page_items()

    # unpack it for clarity of what the objects are
    text_update = page_items_dict['text_info']
    fayette_fig = page_items_dict['fayette_hydrograph']
    multi_fig = page_items_dict['multi_hydrograph']

    fayetteJSON = json.dumps(fayette_fig, cls=plotly.utils.PlotlyJSONEncoder)
    multiJSON = json.dumps(multi_fig, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('index.html',
                            text_update=text_update,
                            fayetteJSON=fayetteJSON,
                            multiJSON=multiJSON)

#-----------------------------------------------------------------------------

# if using the package style format for a flask app, this code is
# called in 'app.py' at the root level of the project and this file is renamed
# to __init__.py

# if __name__ == '__main__':
#     app.run(debug=True)
