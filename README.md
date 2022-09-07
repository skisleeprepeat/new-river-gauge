# dowd-chute-gauge
Virtual streamflow gauge for Fayette Station and the Lower New River Gorge

This project creates a small web app that estimates the streamflow on the New River at Fayette Station for whitewater boaters.  It is a Python Flask application that calls realtime streamflow from other locations in the watershed using the USGS Instantaneous Values Webservice API then estimates flow using a linear regression from other nearby gauge values.
