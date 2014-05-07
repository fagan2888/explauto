from numpy import zeros

from abc import ABCMeta, abstractmethod

from ..utils.config import make_configuration
from ..utils.observer import Observable


class Environment(Observable):
    """ Abstract class to define environments.
        :param array m_mins, m_maxs, s_mins, s_maxs: bounds of the motor (m) and sensory (s) spaces

    """
    __metaclass__ = ABCMeta

    def __init__(self, m_mins, m_maxs, s_mins, s_maxs):
        Observable.__init__(self)

        self.conf = make_configuration(m_mins, m_maxs, s_mins, s_maxs)
        self.state = zeros(self.conf.ndims)

    def update(self, ag_state):
        m = self.compute_motor_command(ag_state)
        self.state[:self.conf.m_ndims] = m

        s = self.compute_sensori_effect()
        self.state[-self.conf.s_ndims:] = s

        self.emit('motor', m)
        self.emit('sensori', s)

    @abstractmethod
    def compute_motor_command(self, ag_state):
        pass

    @abstractmethod
    def compute_sensori_effect(self):
        pass

    # def post_processing(self):
    #     self.state = minimum(self.state, self.bounds[:,1])
    #     self.state = maximum(self.state, self.bounds[:,0])

    def read(self):
        return self.state[self.readable]

    # def write(self, data):
    #     self.state[self.writable] = data

    def dataset(self, orders):
        n = orders.shape[0]
        m_ndims = orders.shape[1]

        data = zeros((n, self.conf.ndims))
        data[:, :m_ndims] = orders

        for i, m in enumerate(orders):
            self.update(m)
            data[i, m_ndims:] = self.state[m_ndims:]

        return data