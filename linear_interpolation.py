
def interpolate(start, end, t):
    return start + t * (end-start)

if __name__ == '__main__':

    # Test

    print(interpolate(0, 1.0, .7))
    print(interpolate(0, 100, .55))
