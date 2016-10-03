import chosenmcplots as cp

c = cp.cs[0]
m = cp.ms[0]
c = c[2].tolist()
m = [ x[7].tolist() for x in m ]

def Windows(series):
  i = 0
  ws = []
  while(i < len(series)):
    if(series[i] == 0.0):
      left = i
      right = i
      while(right < len(series) and series[right] == 0.0):
        right += 1
      w = (left, right - 1)
      ws.append(w)
      i = right
    else:
      i += 1
  return ws

def getMissingWindowDict(windows):
  diff = [(b - a + 1) for (a,b) in windows]
  return cp.Counter(diff)

def InputParameter(p,l,r):
  return 1.0 * (p - l) / (r - l)

''' Cubic Interpolation Functions '''

def CubicInterpolate(p,l,r,series):
  t = InputParameter(p,l,r)
  t2 = t**2
  a0 = series[r+1] - series[r] - series[l-1] + series[l]
  a1 = series[l-1] - series[l] - a0
  a2 = series[r] - series[l-1]
  a3 = series[l]
  return (a0*t*t2 + a1*t2 + a2*t+a3)

''' The CatMull-ROM splines Interpolation  '''

def CatmullRomInterpolate(p,l,r,series):
  t = InputParameter(p,l,r)
  t2 = t**2
  a0 = -0.5*series[l-1] + 1.5*series[l] - 1.5*series[r] + 0.5*series[r+1]
  a1 = series[l-1] - 2.5*series[l] + 2*series[r] - 0.5*series[r+1]
  a2 = -0.5*series[l-1] + 0.5*series[r]
  a3 = series[l]
  return (a0*t*t2 + a1*t2 + a2*t+a3)

''' Hermite Polynomials Interpolation '''

def HermitePolynomials(p,l,r,series,tension,bias):
  t = InputParameter(p,l,r)
  t2 = t**2
  t3 = t2*t
  m0  = (series[l]-series[l-1])*(1+bias)*(1-tension)/2
  m0 += (series[r]-series[l])*(1-bias)*(1-tension)/2
  m1  = (series[r]-series[l])*(1+bias)*(1-tension)/2
  m1 += (series[r+1]-series[r])*(1-bias)*(1-tension)/2
  a0 =  2*t3 - 3*t2 + 1
  a1 =    t3 - 2*t2 + t
  a2 =    t3 -   t2
  a3 = -2*t3 + 3*t2
  return(a0*series[l]+a1*m0+a2*m1+a3*series[r])

