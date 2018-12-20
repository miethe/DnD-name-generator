import os

import matplotlib.pyplot as plt
import torch


def save_model(rnn, model_name):
    os.makedirs("./models", exist_ok=True)
    torch.save(rnn, os.path.join("models", model_name))
    print("Models saved on path: {}".format(os.path.join("models", model_name)))


def load_model(path, device="cuda"):
    print("Loading model from path {}".format(path))
    model = torch.load(path)
    return model.to(device)


def plot_loss(loss):
    plt.plot(loss)
    plt.show()
