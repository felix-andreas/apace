from scipy.optimize import minimize
import numpy as np

def fit_twiss_to_ref_twiss(elements, attributes, linbeamdyn, ref_twiss, method="Nelder-Mead", interpolate=1000):

    def func(params):
        for element, attribute, param in zip(elements, attributes, params):
            setattr(element, attribute, param)

        twiss = linbeamdyn.get_twiss(interpolate=interpolate)
        if not twiss.stable:
            return float("inf")  # 1e3 #TODO: test if better??

        betaxres = twiss.betax_int / ref_twiss.betax_int
        betayres = twiss.betay_int / ref_twiss.betay_int
        betaxres[betaxres < 1] = 1
        betayres[betayres < 1] = 1
        beta_mean_res = np.mean([betaxres, betayres])
        # beta_max = np.max([twiss.betax, twiss.betay])
        # beta_value_max = beta_max / 10

        return beta_mean_res
        # return beta_value_max
        # return beta_mean_res + beta_value_max


    initial_values = [getattr(element, attribute) for element, attribute in zip(elements, attributes)]
    from elements.utils import profile; profile(func, num=100, out_lines=20)(initial_values)
    # result = minimize(func, initial_values, method=method)
    # return result




