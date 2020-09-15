import numpy as np

def randomizeDayVector(mean_func, limit_step=True, squeeze=True):
    
    LENSCALE = 1
    KERNALSHRINK = 100
    NOISESHRINK = 100
    STEP = 0.05
    ZOOM = 1.1
    
    x = np.linspace(0, 23, num = 24, endpoint = True)
    K = np.zeros((len(x), len(x)))
    for i in range(len(x)):
        for j in range(len(x)):
            K[i, j] = np.exp(-1/2*((x[i] - x[j])**2 / LENSCALE)) / KERNALSHRINK
    
    samples = list(np.random.multivariate_normal(mean_func, K, tol=1e-6))
        
    # limit sampled values to [0,1] with step changes
    step_factor = 1 / STEP
    def zeroone(x):
        if x < 0: return 0
        if x > 1: return 1
        return int(x*step_factor + 0.5 ) / step_factor
    def zoom(x):
        return (x - 0.5) * ZOOM + 0.5

    # Bring all values less than 0 up to 0
    samples = [0 if x < 0 else x for x in samples]
    
    if squeeze: samples = [zoom(x) for x in samples]
    if limit_step: samples = [zeroone(x) for x in samples]
        
    return samples