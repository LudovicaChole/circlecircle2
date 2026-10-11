"""Construct a stable revolute basis from the two LS-DYNA rigid-body axes."""
import math


def basis(df, joint):
    if any(n not in df.node for n in joint.nodes):
        raise ValueError(f'Joint {joint.uid}: missing node')
    a,b,c,d = [df.node[n].xyz for n in joint.nodes]
    vector = tuple(c[i]-a[i] for i in range(3))
    length = math.sqrt(sum(v*v for v in vector))
    if length<=1e-14:
        raise ValueError(f'Joint {joint.uid}: zero-length revolute axis')
    axis = tuple(v/length for v in vector)
    other = tuple(d[i]-b[i] for i in range(3))
    norm = math.sqrt(sum(v*v for v in other))
    if norm <=1e-14 or abs(abs(sum(axis[i]*other[i] for i in range(3)))/norm-1)>1e-6:
        raise ValueError(f'Joint {joint.uid}: axes are not parallel')
    if math.dist(a,b)>1e-6*max(1,length) or math.dist(c,d)>1e-6*max(1,length):
        raise ValueError(f'Joint {joint.uid}: revolute node pairs are not coincident')
    helper = min(((1,0,0),(0,1,0),(0,0,1)),key=lambda h:abs(sum(x*y for x,y in zip(axis,h))))
    dot = sum(x*y for x,y in zip(axis,helper))
    second = tuple(helper[i]-dot*axis[i] for i in range(3))
    norm = math.sqrt(sum(v*v for v in second))
    return axis, tuple(v/norm for v in second)
