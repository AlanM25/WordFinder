class Letter:
    def __init__(self, contour, center):
        self.contour = contour
        self.center = center
        self.similarity = []
        self.posibleLetters = []
        
        
    def getCenter(self):
        return self.center
        
    def getContour(self):
        return self.contour
    
    def getLetter(self):
        return self.letter
    
    def getSimilarityValue(self):
        return self.similarity[0]
    
    def setPosibleLetter(self, letter):
    # Si ya hay una de esas letras, no agregar más
        if any(l in self.posibleLetters for l in {'A', 'B', 'C', 'D', 'P', 'Q', 'R'}):
            return  

    # Agregar la letra
        self.posibleLetters.append(letter)

    # Si la letra es una de las especiales, borrar la lista y solo dejar esa
        if letter in {'A', 'B', 'C', 'D', 'P', 'Q', 'R'}:
            self.posibleLetters = [letter] 
            

    
    def containsLetter(self, letter):
        return letter in self.posibleLetters
    
    def getLetter(self):
        return self.letter
    
    
    def setSimilarity(self, data, end):
        key = 0
        val = 0
        count = 0
        for key,val in data.items():
            count += 1
            if(count == end):
                break
        self.letter = key
        self.similarity.append(val)