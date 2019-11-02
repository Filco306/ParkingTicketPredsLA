class Predictor:
    def __init__(self, model_type = ["nn","ensemble","rf","lgbm"]):
        self.model_type = model_type

"""
Idea :

Do a multidimensional, non-parametric bayesian model that basically samples from the multdimensional distribution?

I need a continuous distribution that would give me an estimate, gut what should this distribution be? Probably a

I have, minute by minute, geopoint by geopoint, whether a

In priors, include holidays, people gatherings, stadium locations, parking lots and such

"""

    def serve_prediction(self, start_time, end_time, location, range):
        print("Starting prediction")
