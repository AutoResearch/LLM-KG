import sys, os
import numpy as np
import pandas as pd
from tqdm import tqdm
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
from typing import Union
import numpyro

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.src_rlsindy.resources.bandits import get_update_dynamics


def log_likelihood(data, probs):
    # data: array of binary observations (0 or 1)
    # probs: array of predicted probabilities for outcome 1 
    
    # Sum over all data points and negate the result
    return np.sum(data * np.log(probs))


def bayesian_information_criterion(data, probs, n_parameters, ll=None):
    # data: array of binary observations (0 or 1)
    # probs: array of predicted probabilities for outcome 1
    # n_parameters: integer number of trainable model parameters
    
    if ll is None:
        ll = log_likelihood(data, probs)
    
    return -2 * ll + n_parameters * np.log(len(data))

def akaike_information_criterion(data, probs, n_parameters, ll=None):
    # data: array of binary observations (0 or 1)
    # probs: array of predicted probabilities for outcome 1
    # n_parameters: integer number of trainable model parameters
    
    if ll is None:
        ll = log_likelihood(data, probs)
    
    return -2 * ll + 2 * n_parameters

def get_scores(experiment, agent, n_parameters) -> float:
        probs = get_update_dynamics(experiment, agent)[1]
        ll = log_likelihood(np.eye(2)[experiment.choices.astype(int)], probs)
        bic = bayesian_information_criterion(np.eye(2)[experiment.choices.astype(int)], probs, n_parameters, ll)
        aic = akaike_information_criterion(np.eye(2)[experiment.choices.astype(int)], probs, n_parameters, ll)
        nll = -ll
        return nll, aic, bic
    
def get_scores_array(experiment, agent, n_parameters, verbose=False, save:str=None) -> pd.DataFrame:
        nll, bic, aic = np.zeros((len(experiment))), np.zeros((len(experiment))), np.zeros((len(experiment)))
        ids = range(len(experiment))
        for i in tqdm(ids):
            try:
                nll_i, aic_i, bic_i = get_scores(experiment[i], agent[i], n_parameters[i])
            except ValueError:
                nll_i, aic_i, bic_i = np.nan, np.nan, np.nan
                print(f'Session {i} could not be calculated due to ValueError (most likely SINDy)')
            nll[i] += nll_i
            bic[i] += bic_i
            aic[i] += aic_i
        if verbose:
            print('Summarized statistics:')
            print(f'NLL = {np.sum(np.array(nll))} --- BIC = {np.sum(np.array(bic))} --- AIC = {np.sum(np.array(aic))}')
        df = pd.DataFrame({'Job_ID': ids, 'NLL': nll, 'BIC': bic, 'AIC': aic})
        if save is not None:
            df.to_csv(save, index=False)
        return df