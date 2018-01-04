import vector_sum_talker
from talker import Talker

class VectorSumProxy(Talker):
    def create(self):
        self.talker = vector_sum_talker.VectorSumTalker(*self.args, **self.kwargs)
     
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.create()
        
    def my_name(self):
        return self.talker.my_name()
    
    def get_answer(self, question, *args, **kwargs):
        if question['question'] == 'reset':
            reload(vector_sum_talker)
            self.create()
            return { 'answer': 'vector sum talker has been reset',
                     'score': 1,
                     'state_update': {} }
        return self.talker.get_answer(question, *args, **kwargs)

    @property
    def spellchecker(self):
        return self.talker.spellchecker