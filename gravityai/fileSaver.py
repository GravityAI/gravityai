from abc import ABC, abstractmethod
import os
from fpdf import FPDF

mappings = {
    "txt": "TextFileSaver"
}


class GravityAIOutputHandler(ABC):
    @abstractmethod
    def save(self, result, filename):
        pass



class TextFileSaver(GravityAIOutputHandler):
    def save(self, result, filename):
        with open(f"{filename}.txt", "w") as f:
            f.write(result)
        return f"{filename}.txt"





