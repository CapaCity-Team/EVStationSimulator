class sortedlist(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert(self, element):
        # binary search to find the right position
        lo = 0
        hi = len(self)
        while lo < hi:
            mid = (lo+hi)//2
            if self[mid] < element: lo = mid+1
            else: hi = mid
        super().insert(lo, element)
            
