from datetime import datetime as dt, timedelta, timezone
import dataretrieval.nwis as nwis
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

#----------------------------------------------------------------------------
GAUGE_LIST = ['03185400','03184000','03179000','03176500']

#-----------------------------------------------------------------------------
# Functions used here within gauge_utils.py to make api calls, manipulate
# data, and build charts.
def get_usgs_data(gauge_list):

    '''use the dataretrieval package to get gauge data and return a data frame'''

    # create date strings for today back to 7 days ago
    end_date = dt.today().strftime('%Y-%m-%d')
    start_date = (dt.today() - timedelta(7)).strftime('%Y-%m-%d')
    param_cd = '00060'

    try:
        df = nwis.get_record(sites=gauge_list,
                             service='iv',
                             parameterCd=param_cd,
                             start=start_date,
                             end=end_date
                             ).reset_index().iloc[:,:3]
    except Exception as e:
        df = None
        print("Error: " + repr(e))


    # if a dataframe is returned successfully from USGS, do some formatting
    if df is not None:
        df.replace(-999999.0, pd.to_numeric('x', errors='coerce'), inplace=True)
        df.rename(columns={'00060':'q'}, inplace=True)

    return df


def reformat_data(df):

    ''' pivot dataframe to wideform '''

    dfw = df.pivot(index= 'datetime',
             columns='site_no',
             values='q' )

    return dfw


def estimate_fayette_level(dfw):

    ''' Estimate New River at Fayette Station level using regression from
    New River at Thurmond'''

    print('estimating levels...')

    dfw['fayette_pred'] = round( -3.4 + 0.00155*dfw['03185400'] - 0.0000000905*dfw['03185400']**2 + 0.00000000000226 * dfw['03185400']**3 , 2)

    return dfw

#-----------------------------------------------------------------------------
# Functions used in app.py to return outputs for visualization

def get_text_levels(dfw):

    '''function to return text output for current level information to display
    on website. It should return a dictionary with:
    current level with timestamp,
    change in last hour,
    levels at all other nearby gauges '''

    # get last reading and subtract one hour from it
    try:
      timestamp_last_reading = dfw[~dfw['fayette_pred'].isna()].index.max()
      timestamp_hour_before_last = timestamp_last_reading - timedelta(hours=1)
      last_reading = dfw[dfw.index == timestamp_last_reading]['fayette_pred'].item()
      change_last_hour = dfw[dfw.index == timestamp_last_reading]['fayette_pred'].item() - dfw[dfw.index == timestamp_hour_before_last]['fayette_pred'].item()
      change_last_hour = str(round(change_last_hour, 2))
    except:
      change_last_hour = 'not available'

    # get yesterday's max and min
    try:
        yesterday_data = dfw.loc[(timestamp_last_reading - timedelta(1)).strftime('%Y-%m-%d')]
        peak_flow = round(yesterday_data['fayette_pred'].max(),1)
        min_flow = round(yesterday_data['fayette_pred'].min(),1)

        # get the index value at the max and min flows (returns first row if more than one row is returned)
        peak_time = yesterday_data['fayette_pred'].idxmax()
        min_time =  yesterday_data['fayette_pred'].idxmin()

        yesterday_msg = (f"Yesterday's <strong>peak</strong> level of <strong>{peak_flow}&apos;</strong> occurred at {peak_time.strftime('%I:%M %p')},<br>"
                        f"Yesterday's <strong>low</strong> level of <strong>{min_flow}&apos;</strong> occurred at {min_time.strftime('%I:%M %p')}")

    except:
        yesterday_msg = "Info on yesterday's min/max not available"

    return [round(last_reading,1), timestamp_last_reading.strftime('%I:%M %p'), change_last_hour, yesterday_msg]


def build_7d_chart(dfw):

    ''' Create a hydrograph of estimated levels at Fayette Station for last 7 days'''

    print("Building Fayette Station chart")

    fig = px.line(dfw,
                  x=dfw.index,
                  y=dfw.fayette_pred,
                  labels={
                         "datetime": "",
                         "fayette_pred": "Feet",
                     },
                  title="Estimated Fayette Station Level</i>")

    fig.update_traces(line=dict(color="Blue", width=2))

    y_max = dfw['fayette_pred'].max()
    y_min = dfw['fayette_pred'].min()

    # add background shading ranges for difficult
    fig.add_hrect(y0=10, y1=20, line_width=0, fillcolor="red", opacity=0.15)
    fig.add_hrect(y0=6, y1=10, line_width=0, fillcolor="black", opacity=0.15)
    fig.add_hrect(y0=2, y1=6, line_width=0, fillcolor="blue", opacity=0.15)
    fig.add_hrect(y0=-2, y1=2, line_width=0, fillcolor="green", opacity=0.15)

    # add some horizontal guidelines
    fig.add_hline(y=-1.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=-0.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=0.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=1.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=2.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=3.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=4.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=5.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=6.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=7.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=8.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=9.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=10.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=11.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)
    fig.add_hline(y=12.5, line_width=0.5, line_dash="dash", line_color="white", opacity=0.5)

    fig.update_layout(
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="Tahoma"
        )
    )

    # print("plotly express hovertemplate:", fig.data[0].hovertemplate)
    fig.update_traces(hovertemplate="%{y:.1f} '<br>%{x|%I:%M %p}")

    # fig.update_yaxes(tick0=0, dtick=0.5)
    fig.update_yaxes(tickvals=[-2,-1,0,1,2,3,4,5,6,7,8,9,10,11,12],
                     ticks="outside",
                     ticklen=5)
    fig.update_layout(yaxis_range=[min(y_min-0.5,-2), max(y_max+1,8)]) #keep the y axis at 0-5 feet unless water is really high or low
    fig.update_layout(title_x=0.5) #center title
    fig.update_xaxes(
        tickformat="%m-%d",
        tickangle = 67.5
        )
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        paper_bgcolor='#EEEEEE'
        )
    config = {'displayModeBar': False}

    return fig


def build_area_gauges_chart(df):

    '''return a plotly chart of hydrograph for all gauges for last 7 days'''

    print("Building multi-gauge chart")

    plot_df = df
    # rename the site number columes with common local names
    # create plain-named aliases for gauges
    name_dict = {'03185400':'New @ Thurmond     ',
                 '03176500':'New @ Glen Lyn, VA',
                 '03179000':'Bluestone @ Pipestem      ',
                 '03184000':'Greenbrier @ Hilldale  ',
    }
    plot_df = plot_df.replace({"site_no": name_dict})

    # make the plot

    # create lists of formatted dates for x-axis so that axis and hovertemplate can be formatted separately
    # end_date = dt.today().strftime('%Y-%m-%d')
    # start_date = (dt.today() - timedelta(7)).strftime('%Y-%m-%d')
    end_date = dt.today()
    start_date = (dt.today() - timedelta(7))
    print(f'start: {start_date, end_date}')
    # xtickvals = [dt.datetime(date) for date in range(start_date, end_date)]
    xtickvals = [(start_date + timedelta(days = day)) for day in range(7)]
    print(xtickvals)
    xticktext = [val.strftime('%m-%d') for val in xtickvals]
    print(xticktext)

    fig = px.line(plot_df,
              x="datetime",
              y="q",
              color='site_no',
              labels={
                  "datetime": "",
                  "q": "Flow (cfs)",
                  },
              title="New River Area Gauges",
              )
    # hover controls and settings
    fig.update_traces(hovertemplate="%{y:.0f} cfs")
    fig.update_layout(hovermode="x unified")
    # legend formatting options
    fig.update_layout(legend=dict(
        orientation="h",
        yanchor='top',
        y=-0.2,
        xanchor="right",
        x=1,
        title_text='',
    ))
    #center title
    fig.update_layout(
        title_x=0.5,
    )
    # format x-axis dates
    fig.update_xaxes(
        tickformat="%m-%d %H:%M",
        tickangle = 67.5,
        ticktext=xticktext,
        tickvals=xtickvals
    )
    # decrease the paper margin space around ove the plot to bring the title closer
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20)
        )
    fig.update_layout({
        'paper_bgcolor': '#EEEEEE',
        'plot_bgcolor': '#FFF'
        # 'plot_bgcolor': 'rgba(204,209,217,0.25)'
        })

    return fig

#-----------------------------------------------------------------------------
# Control flow

def create_page_items():

    gauge_data = get_usgs_data(GAUGE_LIST)
    # print(gauge_data.head())

    try:
        wide_data = reformat_data(gauge_data)
        wide_data = estimate_fayette_level(wide_data)
    except:
        wide_data = None

    # print(wide_data.head())
    try:
        text_info = get_text_levels(wide_data)
    except:
        text_info = None

    try:
        fayette_hydrograph = build_7d_chart(wide_data)
    except:
        fayette_hydrograph = None

    try:
        multi_hydrograph = build_area_gauges_chart(gauge_data)
    except:
        multi_hydrograph = None

    return {'text_info': text_info,
            'fayette_hydrograph': fayette_hydrograph,
            'multi_hydrograph': multi_hydrograph,
            }
