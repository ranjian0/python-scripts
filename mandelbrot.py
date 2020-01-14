import numpy as np
from PIL import Image


def mandelbrot(size=(250, 250), iterations=100, 
                boundsx=(-2, 1), boundsy=(-1, 1)):
                    
    m, n = size
    x = np.linspace(*boundsx, num=m).reshape((1, m))
    y = np.linspace(*boundsy, num=n).reshape((n, 1))
    C = np.tile(x, (n, 1)) + 1j * np.tile(y, (1, m))

    Z = np.zeros((n, m), dtype=complex)
    M = np.full((n, m), True, dtype=bool)

    I = np.zeros((n, m), dtype=int)
    for i in range(iterations):
        Z[M] = Z[M] * Z[M] + C[M]
        M[np.abs(Z) > 2] = False
        I[np.abs(Z) < 2] = i
        print(f"{(1+i)/iterations:.2%}")


    # -- saturation
    S = np.sqrt(I / iterations)

    TRUE_COLOR = np.ones((n, m, 3), dtype=float)
    TRUE_COLOR[:, :, 0] *= 0.3
    TRUE_COLOR[:, :, 1] = S

    COLOR = np.zeros((n, m, 3), dtype=float)
    COLOR[I < iterations-1] = TRUE_COLOR[I < iterations-1]
    return Image.fromarray(np.uint8(COLOR * 255))
    
img = mandelbrot(size=(2000, 2000), iterations=5000)
img.save("mandel.png")
# ~ img.show()
