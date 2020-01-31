# -*- coding: utf-8 -*-
"""
Created on Fri Apr 08 00:42:29 2016

@author: itithilien
"""

from math import sqrt, log, pi, exp
from scipy.stats import norm

def BSM(optionType, spot, strike, ttm, riskFree, divYield, volatility):
    s, k, t, rf, q, v = spot, strike, ttm, riskFree, divYield, volatility
    
    if optionType == "call" :
        cp = 1
    elif optionType == "put":
        cp = -1
    else:
        raise TypeError("Option type flag incorrectly set; set it as either `call` or `put` ")
    
    d1 = (log(s/k)+(rf-q+0.5*v**2)*t)/(v*sqrt(t))
    d2 = d1 - v*sqrt(t)
    price = cp*s*exp(-q*t)*norm.cdf(cp*d1) - cp*k*exp(-rf*t)*norm.cdf(cp*d2)
    
    return price

def impVol(optionType, OptPrice, spot, strike, ttm, riskFree, divYield, tolerance = 1e-8):
    """
    Calculates implied volatility using Newton-Raphson method
    
    Ex: impVol("call", 1.52, 23.95, 24, 71.0/365, 0.05)
    """
    price, s, k, t, rf, q = OptPrice, spot, strike, ttm, riskFree, divYield
    if optionType == "call" :
        cp = 1
    elif optionType == "put":
        cp = -1
    else:
        raise TypeError("Option type flag incorrectly set; set it as either `call` or `put` ")
    
    v = sqrt(2*pi/t)*price/s
    #print "initial volatility: ",v
    for i in range(1, 100):
        d1 = (log(s/k)+(rf-q+0.5*v**2)*t)/(v*sqrt(t))
        d2 = d1 - v*sqrt(t)
        vega = s*norm.pdf(d1)*sqrt(t)*exp(-q*t)
        price0 = cp*s*exp(-q*t)*norm.cdf(cp*d1) - cp*k*exp(-rf*t)*norm.cdf(cp*d2)
        v = v - (price0 - price)/vega
        #print "price, vega, volatility\n",(price0, vega, v)
        if abs(price0 - price) < tolerance :
            break
    return v

    
def greeksOrder1(optionType, spot, strike, riskFree, ttm, vol, divYield=0):
    
    rf, t, v = riskFree, ttm, vol #spot, strike, divYield, 
    d1 = (log(spot/strike) + t*(rf - divYield + v*v/2))/(v*sqrt(t))
    d2 = d1 - v*sqrt(t)
    
    if optionType == "call" :
        # for call : 1st order
        price = spot * exp(-divYield * t) * norm.cdf(d1) - strike * exp(-rf * t)* norm.cdf(d2)
        delta = exp(-divYield*t)*norm.cdf(d1)
        vega = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)
        theta = divYield * spot * exp(-divYield * t) * norm.cdf(d1) - spot * exp(-divYield * t) * norm.pdf(d1)/2 * v/sqrt(t) - rf * strike * exp(-rf * t) * norm.cdf(d2)
        rho = t * strike * exp(-rf * t)* norm.cdf(d2)
        Lambda = delta * spot/price
        dualDelta = -exp(-rf * t)* norm.cdf(d2)
    
    elif optionType == "put" :
        # for put : 1st order
        price = -spot * exp(-divYield * t) * norm.cdf(-d1) + strike * exp(-rf * t) * norm.cdf(-d2)
        delta = -exp(-divYield*t) * norm.cdf(-d1)
        vega = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)
        theta = -divYield * spot * exp(-divYield * t) * norm.cdf(-d1) - spot * exp(-divYield * t) * norm.pdf(d1)/2 * v/sqrt(t) + rf * strike * exp(-rf * t) * norm.cdf(-d2)
        rho = -t * strike * exp(-rf * t) * norm.pdf(-d2)
        Lambda = delta * spot/price
        dualDelta = exp(-rf * t)* norm.cdf(-d2)
    
    else:
        raise TypeError("Option type flag incorrectly set")
    
    return {"price":price, "delta":delta, "vega":vega, "theta":theta, "rho":rho, "Lambda":Lambda, "dualDelta":dualDelta}

def greeksOrder2(optionType, spot, strike, riskFree, ttm, vol, divYield=0):
    
    rf, t, v = riskFree, ttm, vol #spot, strike, divYield, 
    d1 = (log(spot/strike) + t*(rf - divYield + v*v/2))/(v*sqrt(t))
    d2 = d1 - v*sqrt(t)
    
    gamma = exp(-divYield * t) * norm.pdf(d1)/(spot * v * sqrt(t))
    vanna = -exp(-divYield * t) * norm.pdf(d1) * d2/v
    veta = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t) * (divYield + (rf - divYield)*d1/(v*sqrt(t)) - (1+d1*d2)/(2*t))
    vomma = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t) * d1*d2/v
    dualGamma = exp(-rf * t)* norm.pdf(d2) / (strike * v * sqrt(t))
    
    if optionType == "call" :
        charm = divYield * exp(-divYield * t) * norm.cdf(d1) - exp(-divYield * t) * norm.pdf(d1) * (2*(rf - divYield)*t - d2*v*sqrt(t))/(2*v*t*sqrt(t))
    elif optionType == "put" :
        charm = -divYield * exp(-divYield * t) * norm.cdf(-d1) - exp(-divYield * t) * norm.pdf(d1) * (2*(rf - divYield)*t - d2*v*sqrt(t))/(2*v*t*sqrt(t))
    else:
        raise TypeError("Option type flag incorrectly set")
    
    return [gamma, vanna, charm, veta, vomma, dualGamma]


def greeksOrder3(optionType, spot, strike, riskFree, ttm, vol, divYield=0):
    
    rf, t, v = riskFree, ttm, vol #spot, strike, divYield, 
    d1 = (log(spot/strike) + t*(rf - divYield + v*v/2))/(v*sqrt(t))
    d2 = d1 - v*sqrt(t)
    
    if optionType == "call" or optionType == "put" :
        speed = -exp(-divYield * t) * norm.pdf(d1)/(spot*spot * v * sqrt(t)) * (1 + d1/(v * sqrt(t)))
        zomma = exp(-divYield * t) * norm.pdf(d1) * (d1*d2 -1)/(spot * v*v * sqrt(t))
        color = -exp(-divYield * t) * norm.pdf(d1) / (2*spot*v*t*sqrt(t)) * (1 + 2*t*divYield + 2*(rf - divYield)*d1*sqrt(t)/v - d1 *d2)
        ultima = -spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)/(v*v) * (d1**2 + d2**2 + d1*d2 - d1**2*d2**2)
    
    else:
        raise TypeError("Option type flag incorrectly set")
    
    return [speed, zomma, color, ultima]

def greeksAll(optionType, spot, strike, riskFree, ttm, vol, divYield=0, flag="list"):
    
    rf, t, v = riskFree, ttm, vol #spot, strike, divYield, 
    d1 = (log(spot/strike) + t*(rf - divYield + v*v/2))/(v*sqrt(t))
    d2 = d1 - v*sqrt(t)
    
    gamma = exp(-divYield * t) * norm.pdf(d1)/(spot * v * sqrt(t))
    vanna = -exp(-divYield * t) * norm.pdf(d1) * d2/v
    veta = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t) * (divYield + (rf - divYield)*d1/(v*sqrt(t)) - (1+d1*d2)/(2*t))
    vomma = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t) * d1*d2/v
    dualGamma = exp(-rf * t)* norm.pdf(d2) / (strike * v * sqrt(t))
    speed = -exp(-divYield * t) * norm.pdf(d1)/(spot*spot * v * sqrt(t)) * (1 + d1/(v * sqrt(t)))
    zomma = exp(-divYield * t) * norm.pdf(d1) * (d1*d2 -1)/(spot * v*v * sqrt(t))
    color = -exp(-divYield * t) * norm.pdf(d1) / (2*spot*v*t*sqrt(t)) * (1 + 2*t*divYield + 2*(rf - divYield)*d1*sqrt(t)/v - d1 *d2)
    ultima = -spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)/(v*v) * (d1**2 + d2**2 + d1*d2 - d1**2*d2**2)
    
    if optionType == "call" :
        price = spot * exp(-divYield * t) * norm.cdf(d1) - strike * exp(-rf * t)* norm.cdf(d2)
        delta = exp(-divYield*t)*norm.cdf(d1)
        vega = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)
        theta = divYield * spot * exp(-divYield * t) * norm.cdf(d1) - spot * exp(-divYield * t) * norm.pdf(d1)/2 * v/sqrt(t) - rf * strike * exp(-rf * t) * norm.cdf(d2)
        rho = t * strike * exp(-rf * t)* norm.cdf(d2)
        Lambda = delta * spot/price
        dualDelta = -exp(-rf * t)* norm.cdf(d2)
        charm = divYield * exp(-divYield * t) * norm.cdf(d1) - exp(-divYield * t) * norm.pdf(d1) * (2*(rf - divYield)*t - d2*v*sqrt(t))/(2*v*t*sqrt(t))
    
    elif optionType == "put" :
        price = -spot * exp(-divYield * t) * norm.cdf(-d1) + strike * exp(-rf * t) * norm.cdf(-d2)
        delta = -exp(-divYield*t) * norm.cdf(-d1)
        vega = spot * exp(-divYield * t) * norm.pdf(d1) * sqrt(t)
        theta = -divYield * spot * exp(-divYield * t) * norm.cdf(-d1) - spot * exp(-divYield * t) * norm.pdf(d1)/2 * v/sqrt(t) + rf * strike * exp(-rf * t) * norm.cdf(-d2)
        rho = -t * strike * exp(-rf * t) * norm.pdf(-d2)
        Lambda = delta * spot/price
        dualDelta = exp(-rf * t)* norm.cdf(-d2)
        charm = -divYield * exp(-divYield * t) * norm.cdf(-d1) - exp(-divYield * t) * norm.pdf(d1) * (2*(rf - divYield)*t - d2*v*sqrt(t))/(2*v*t*sqrt(t))
    
    else:
        raise TypeError("Option type flag incorrectly set")
    
    if flag == "list" :
        return [price, delta, vega, theta, rho, Lambda, dualDelta, gamma, vanna, charm, veta, vomma, dualGamma, speed, zomma, color, ultima]
    elif flag == "dict" :
        return {"price":price, "delta":delta, "vega":vega, "theta":theta, "rho":rho, "Lambda":Lambda, "dualDelta":dualDelta, "gamma":gamma, "vanna":vanna, "charm":charm, "veta":veta, "vomma":vomma, "dualGamma":dualGamma, "speed":speed, "zomma":zomma, "color":color, "ultima":ultima}
    else:
        print("set proper output flag")
        return -1
    
    
    

    

    
    return {"price":price, "delta":delta, "vega":vega, "theta":theta, "rho":rho, "Lambda":Lambda, "dualDelta":dualDelta, "gamma":gamma, "vanna":vanna, "charm":charm, "veta":veta, "vomma":vomma, "dualGamma":dualGamma, "speed":speed, "zomma":zomma, "color":color, "ultima":ultima}

