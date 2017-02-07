from adversaries.adversary import Adversary
from data_reader.input import Instance, FeatureVector
from typing import List, Dict
from learners.learner import InitialPredictor
from learners.models.model import BaseModel
from classifier import Classifier
from copy import deepcopy
from math import exp

'''Simple optimization of adversarial instance.

Concept:
    Iterates through features in the adversarial instance, flipping features
    that lower the probability of being classified adversarial.
'''

class SimpleOptimize(Adversary):

    def __init__(self, lambda_val=-100,max_change=1000,learner=None):
        self.lambda_val = lambda_val                     # type: float
        self.max_change = max_change                     # type: float
        self.num_features = None                         # type: int
        self.learn_model = learner  	                 #type: Classifier


    def attack(self, instances: List[Instance]) -> List[Instance]:
        transformed_instances = []
        if self.num_features == None:
            self.num_features = instances[0].get_feature_vector().get_feature_count()
        for instance in instances:
            transformed_instance = deepcopy(instance)
            if instance.get_label() == 1:
                transformed_instances.append(self.optimize(transformed_instance))
            else:
                transformed_instances.append(transformed_instance)
        return transformed_instances

    def set_params(self, params: Dict):
        if 'lambda_val' in params.keys():
            self.lambda_val = params['lambda_val']
        if 'max_change' in params.keys():
            self.max_change = params['max_change']

    def get_available_params(self) -> Dict:
        params = {'lambda_val': self.lambda_val,
                  'max_change': self.max_change}
        return params

    def set_adversarial_params(self, learner, train_instances: List[Instance]):
        self.learn_model = learner
        self.num_features = train_instances[0].get_feature_vector().get_feature_count()

    def optimize(self, instance: Instance):
        change = 0
        for i in range(0, self.num_features):
            orig_prob = self.learn_model.decision_function([instance])[0]
            instance.get_feature_vector().flip_bit(i)
            change += 1
            new_prob = self.learn_model.decision_function([instance])[0]
            if new_prob >= (orig_prob-exp(self.lambda_val)):
                instance.get_feature_vector().flip_bit(i)
                change -= 1
            if change > self.max_change:
                break
        return instance

    def __copy__(self):
        adv = type(self)()
        adv.__dict__.update(self.__dict__)
        return adv

    def __deepcopy__(self, memo):
        deepcopy_method = self.__deepcopy__
        self.__deepcopy__ = None
        new_a = deepcopy(self, memo)
        self.__deepcopy__ = deepcopy_method

        new_a.learner = None
        new_a.num_features = None
        return new_a

    def clone(self):
        """return a custom deepcopy of the adversary."""
        return deepcopy(self)
