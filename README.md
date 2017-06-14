# UQ Final #

UQ Final is a tool which helps students calculate what grades they need to get on their assessment in order to achieve a desired grade in courses at [The University of Queensland](http://www.uq.edu.au/).

You can use the tool at [uqfinal.com](https://uqfinal.com).

UQ Final is not associated with The University of Queensland.

## Software Structure ##
The app is in two parts, the fully-static webapp and the Python api which powers it.

### Webapp ###
The webapp found in the `/site` directory is fully static and is served to the users with S3 and Cloudfront.

You can contribute to the webapp in simple Javascript, HTML and LESS without any required knowledge of templating or server side code.
The site can be run locally and is configured to point to the production API.
The core files for contribution in this area are `index.html`, `app.less` and `app.js`.

### API ###
The API found in the `/api` directory is a Python Flask app which is served by AWS Lambda and API Gateway in production.

To run the API locally you need to install it using `pip install .`.
You will then need a DynamoDB table `uqfinal-offerings` and have your connection settings for AWS configured locally.

The API is structured as if the whole app is just a cache over some function of the UQ website.
You can add new functionality simply by defining how it should be "calculated". See the `models.py` for how this works.