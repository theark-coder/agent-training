class TextProcessor:
    def normalize(self,text:str)->str:
        return text.lower()
    def word_count(self, text:str) -> int:
        text=self.normalize(text)
        words=text.split()
        return len(words)
    def most_common_words(self, text:str, k:int=5)-> list[tuple[str,int]]:
        words=self.normalize(text).split()
        counts={}
        for word in words:
            counts[word]=counts.get(word,0) + 1
        sorted_words=sorted(counts.items(),
        key=lambda item:item[1],
        reverse=True,)
        return  sorted_words[:k]