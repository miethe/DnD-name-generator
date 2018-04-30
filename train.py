import os
import os.path as osp

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.optim import RMSprop
from torch.utils.data import DataLoader

from torchvision.transforms import Compose

from data import DnDCharacterNameDataset, Vocabulary, OneHot


class RNN(nn.Module):
    def __init__(self, input_size, hidden_size, output_size):
        super(RNN, self).__init__()
        self.lstm_cell = nn.LSTMCell(input_size, hidden_size)
        self.dense = nn.Linear(hidden_size, output_size)
        self.softmax = nn.Softmax(dim=1)

    def forward(self, inputs):
        hx = torch.randn((1, self.lstm_cell.hidden_size))
        cx = torch.randn((1, self.lstm_cell.hidden_size))

        outputs = torch.empty_like(inputs)
        for idx, input in enumerate(inputs):
            hx, cx = self.lstm_cell(input, (hx, cx))
            logits = self.dense(hx)
            output = self.softmax(logits)

            outputs[idx] = output

        return F.softmax(outputs)


def train(epochs, hidden_size, model_name):
    vocab = Vocabulary()

    train_loder = DataLoader(dataset=DnDCharacterNameDataset(root_dir="./data",
                                                             transform=Compose([vocab,
                                                                                OneHot(len(vocab))]),
                                                             target_transform=Compose([vocab,
                                                                                       OneHot(len(vocab))])))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    rnn = RNN(input_size=len(vocab),
              hidden_size=hidden_size,
              output_size=len(vocab))

    optimizer = RMSprop(rnn.parameters())

    for epoch in range(epochs):
        print("Epoch {}/{}".format(epoch+1, epochs))
        print('-' * 10)

        optimizer.zero_grad()

        running_loss = 0
        for input, target in train_loder:
            input = input.transpose(1, 0).float()
            target = target.squeeze().long()

            output = rnn(input)
            loss = F.nll_loss(output, target)
            loss.backward()
            optimizer.step()

            running_loss += loss.item()

        print("Loss {:.4f}\n".format(running_loss/len(train_loder)))

    os.makedirs("./models", exist_ok=True)
    torch.save(rnn, osp.join("models", model_name))


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('-e', '--epochs', default=100)
    parser.add_argument('-hs', '--hidden_size', default=128)
    parser.add_argument('-m', '--model_name', default='model_cuda.pt')
    args = parser.parse_args()

    train(epochs=args.epochs,
          hidden_size=args.hidden_size,
          model_name=args.model_name)