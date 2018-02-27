import tensorflow as tf
import numpy as np

from neupy.utils import asfloat
from neupy.core.properties import ProperFractionProperty, NumberProperty
from .base import MinibatchGradientDescent


__all__ = ('Adadelta',)


class Adadelta(MinibatchGradientDescent):
    """
    Adadelta algorithm.

    Parameters
    ----------
    decay : float
        Decay rate. Value need to be between ``0``
        and ``1``. Defaults to ``0.95``.

    epsilon : float
        Value need to be greater than ``0``
         Defaults to ``1e-5``.

    {MinibatchGradientDescent.Parameters}

    Attributes
    ----------
    {MinibatchGradientDescent.Attributes}

    Methods
    -------
    {MinibatchGradientDescent.Methods}

    Examples
    --------
    >>> import numpy as np
    >>> from neupy import algorithms
    >>>
    >>> x_train = np.array([[1, 2], [3, 4]])
    >>> y_train = np.array([[1], [0]])
    >>>
    >>> mnet = algorithms.Adadelta((2, 3, 1))
    >>> mnet.train(x_train, y_train)
    """
    decay = ProperFractionProperty(default=0.95)
    epsilon = NumberProperty(default=1e-5, minval=0)

    def init_param_updates(self, layer, parameter):
        step = self.variables.step
        epsilon = self.epsilon

        prev_mean_squred_grad = tf.get_variable(
            "{}/prev-mean-squred-grad".format(parameter.op.name),
            parameter.shape,
            dtype=tf.float32,
            initializer=tf.zeros_initializer,
        )
        prev_mean_squred_dx = tf.get_variable(
            "{}/prev-mean-squred-dx".format(parameter.op.name),
            parameter.shape,
            dtype=tf.float32,
            initializer=tf.zeros_initializer,
        )

        gradient, = tf.gradients(self.variables.error_func, parameter)

        mean_squred_grad = (
            self.decay * prev_mean_squred_grad +
            (1 - self.decay) * gradient ** 2
        )
        parameter_delta = gradient * (
            tf.sqrt(prev_mean_squred_dx + epsilon) /
            tf.sqrt(mean_squred_grad + epsilon)
        )
        mean_squred_dx = (
            self.decay * prev_mean_squred_dx +
            (1 - self.decay) * parameter_delta ** 2
        )

        return [
            (prev_mean_squred_grad, mean_squred_grad),
            (prev_mean_squred_dx, mean_squred_dx),
            (parameter, parameter - step * parameter_delta),
        ]
