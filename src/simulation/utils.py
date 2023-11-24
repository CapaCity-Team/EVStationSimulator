class sortedlist(list):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def insert(self, element):
        for i in range(len(self)):
            if self[i] > element:
                super().insert(i, element)
                return
        self.append(element)
            
