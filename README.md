# Flask
this repo was made for deploying the flask api to AWS ec2 instance, it is a part of the coin recognition project. 
## working
this contains a flask app which has a post API endpoint defined, it also has a setup function which runs once when you start the server and loads the model file and details file in the ram.
the post api accepts requests with two image files in .jpg with keys 'front' and 'back' for front and back side of the coin. along with two image files it also demands a header named 'key' which should contain an api access key to authorize the api usage.
the api takes the two images and runs an inference on the model, the model returns a class number for the predicted class, we then fetch details against the predicted class number from the data loaded from 'details.csv'. we than combine this info and send it as json response.

## how to run
to run this project you need three things:
  1) model weights file in .hdf5 format.
  2) coinDetails.csv file which contains details for the coins.
  3) .env file which has a variable VALID_API_KEY defined in it.

put these three files in the project directory and run the *api.py* file. (to run this locally, you need a system with at least 16 gb RAM)
runing this file might take a couple minutes as the setup() function runs for the first time and loads the model file and you might also see some tensorflow memory warnings.
after the server is finished starting up you can run the *testClient.py* file after setting the url and images paths, it will print whatever response is returned from the server.
