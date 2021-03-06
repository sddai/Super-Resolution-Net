import argparse

import keras.backend as K
from keras.layers import Input, Conv2D, Add
from keras.models import Model
from keras.utils import plot_model

import utils
from config import img_size, channel, kernel


def build_model(scale, num_layers=32, feature_size=256, scaling_factor=0.1):
    input_tensor = Input(shape=(img_size, img_size, channel))

    # One convolution before res blocks and to convert to required feature depth
    x = Conv2D(feature_size, (kernel, kernel), activation='relu', padding='same', name='conv1')(input_tensor)

    # Store the output of the first convolution to add later
    conv_1 = x

    """
    This creates `num_layers` number of resBlocks
    a resBlock is defined in the paper as
    (excuse the ugly ASCII graph)
    x
    |\
    | \
    |  conv2d
    |  relu
    |  conv2d
    | /
    |/
    + (addition here)
    |
    result
    """

    """
    Doing scaling here as mentioned in the paper:
    `we found that increasing the number of feature
    maps above a certain level would make the training procedure
    numerically unstable. A similar phenomenon was
    reported by Szegedy et al. We resolve this issue by
    adopting the residual scaling with factor 0.1. In each
    residual block, constant scaling layers are placed after the
    last convolution layers. These modules stabilize the training
    procedure greatly when using a large number of filters.
    In the test phase, this layer can be integrated into the previous
    convolution layer for the computational efficiency.'
    """

    # Add the residual blocks to the model
    for i in range(num_layers):
        x = utils.res_block(x, feature_size, scale=scaling_factor)

    x = Conv2D(feature_size, (kernel, kernel), padding='same')(x)
    x = Add()([x, conv_1])

    # Upsample output of the convolution
    x = utils.upsample(x, scale, feature_size)

    outputs = x

    model = Model(inputs=input_tensor, outputs=outputs, name="EDSR")
    return model


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument("-s", "--scale", help="scale")
    args = vars(ap.parse_args())
    scale = int(args["scale"])
    m = build_model(scale)
    print(m.summary())
    plot_model(m, to_file='model.svg', show_layer_names=True, show_shapes=True)
    K.clear_session()
