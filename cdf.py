#!/usr/bin/python

import math
import Gnuplot
import Gnuplot.funcutils
from   numpy import arange

def erf(x,steps=100):
    """
    Compute the error function, erf, for the normal distribution

    erf(x)  = 2/sqrt(pi) * integral from 0->x of e^(-t^2) dt
    """
    if x == 0:
        return 0

    if x < 0:
        return -erf(-x, steps)

    halfstep = x / (2.0 * steps)

    trange    = [halfstep+(x*i/float(steps)) for i in range(steps)]
    exponent  = [-(t*t) for t in trange]
    function  = [math.pow(math.e, exp) for exp in exponent]
    integral  = [f*x/float(steps) for f in function]
    scaled    = sum(integral) * 2 / math.sqrt(math.pi)
    return scaled


def cdf(x, mu, sigma):
    """
    Return the cummulative distribution:

    probability(random.normal_distibution(mu, sigma) <= x)
    """
    return (1 + erf((x-mu)/(sigma*math.sqrt(2)))) / 2.0


def main():
    mu    = arange(-100, 101)
    sigma = 250 - 3*arange(2, 63)
    
    def prob_home_win(x,y):
        return 1-cdf(0,x,y)
    
    g = Gnuplot.Gnuplot(debug=1)
    g('set parametric')
    g('set data style lines')
    g('set hidden')
    g('set contour base')
    g('set terminal wxt enhanced')
    g.title('P_{Home Win}')
    g.xlabel('{/Symbol m} (BP_{Home} - BP_{Away})')
    g.ylabel('{/Symbol s}')
    g('set xtics ("-90" -90, "-45" -45, "0" 0, "45" 45, "90" 90)')
    g('set ytics ("Many Connections" 65, "Few Connections" 235)')
    g('set ztics ("0.25" 0.25, "0.50" 0.5, "0.75" 0.75, "1.00" 1)')
    g('set view 70, 10, 1, 1')
    g.splot(Gnuplot.funcutils.compute_GridData(mu, sigma, prob_home_win, binary=0))
    raw_input('Press ENTER')
    g.hardcopy('cdf.svg', terminal='svg', enhanced=True)


if __name__ == "__main__":
    main()
